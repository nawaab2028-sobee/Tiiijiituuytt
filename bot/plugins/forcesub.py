# ─────────────────────────────────────────────────────────────────────────
# Force Subscribe
#  - Every channel in Config.FORCE_SUB_CHANNELS must be joined to use the bot
#  - The check runs before EVERY private message / command / button press
#    (/start, /login, /upload, /help ... everything)
#  - Users who joined are SAVED (fs_members.json) so they survive restarts
#  - When a saved user leaves a channel, the bot DMs them immediately:
#      1) instantly, through Telegram chat member updates
#      2) as a backup, through a periodic membership sweep
#  - A personal single-use invite link is created for every user
# ─────────────────────────────────────────────────────────────────────────
import asyncio
import html
import json
import logging
import re
import threading
import time
from datetime import datetime, timedelta

from pyrogram import filters as Filters
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from ..config import Config
from ..utubebot import UtubeBot

log = logging.getLogger(__name__)

OWNER_ID = Config.OWNER_ID
FORCE_SUB_ENABLED = bool(Config.FORCE_SUB_ENABLED)
EXEMPT_OWNER = bool(Config.FORCE_SUB_EXEMPT_OWNER)
SWEEP_SECONDS = int(Config.FORCE_SUB_SWEEP_SECONDS)
FS_FILE = "fs_members.json"

INVITE_TTL_SEC = 24 * 60 * 60   # personal invite link is valid for 24 hours
ALERT_GAP_SEC = 6 * 60 * 60     # same owner alert at most once per 6 hours
LEFT_DM_GAP_SEC = 10 * 60       # never DM the same user+channel twice within 10 minutes
PROMPT_GAP_SEC = 3              # do not spam the prompt if the user sends many messages
PASS_CACHE_SEC = 15             # a user who just passed is not re-checked for 15 seconds


# ── Read channels from config (placeholder / invalid chat_id are ignored) ──
def _load_channels():
    channels, skipped = [], []
    for i, c in enumerate(getattr(Config, "FORCE_SUB_CHANNELS", None) or []):
        if not isinstance(c, dict):
            continue
        raw = str(c.get("chat_id", "")).strip()
        title = str(c.get("title") or f"Channel {i + 1}").strip()
        if not re.fullmatch(r"-100\d{6,}", raw):
            skipped.append(title)
            continue
        channels.append(
            {"title": title, "link": str(c.get("link") or "").strip(), "chat_id": int(raw)}
        )
    if skipped:
        log.warning(f"[ForceSub] chat_id not filled, channels ignored: {', '.join(skipped)}")
    return channels


CHANNELS = _load_channels()
BY_ID = {c["chat_id"]: c for c in CHANNELS}


def enabled() -> bool:
    return FORCE_SUB_ENABLED and bool(CHANNELS)


def is_exempt(user_id: int) -> bool:
    return EXEMPT_OWNER and user_id == OWNER_ID


# ── Saved "this user joined this channel" records (JSON file) ──
_lock = threading.Lock()


def _read_store() -> dict:
    try:
        with open(FS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_store(data: dict) -> None:
    try:
        with open(FS_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        log.error(f"[ForceSub] saving {FS_FILE} failed: {e}")


def mark_joined(user_id: int, chat_id: int) -> None:
    with _lock:
        data = _read_store()
        users = data.setdefault(str(chat_id), [])
        if user_id not in users:
            users.append(user_id)
            _write_store(data)


def unmark(user_id: int, chat_id: int) -> None:
    with _lock:
        data = _read_store()
        users = data.get(str(chat_id), [])
        if user_id in users:
            users.remove(user_id)
            _write_store(data)


def saved_records() -> list:
    with _lock:
        data = _read_store()
    out = []
    for cid, users in data.items():
        try:
            chat_id = int(cid)
        except ValueError:
            continue
        if chat_id in BY_ID:
            out.extend((chat_id, uid) for uid in users)
    return out


# ── helpers ──
_LINK_CACHE = {}    # (chat_id, user_id) -> (url, expires_at)
_ALERTED_AT = {}
_LEFT_DM_AT = {}
_PROMPT_AT = {}
_PASSED_AT = {}


def _status(member) -> str:
    """Normalised status that works on every Pyrogram version (str or enum)."""
    raw = getattr(member, "status", "")
    name = str(getattr(raw, "name", raw)).lower()
    name = name.split(".")[-1]
    return {"creator": "owner", "kicked": "banned"}.get(name, name)


def _is_in(member) -> bool:
    if member is None:
        return False
    st = _status(member)
    if st in ("owner", "administrator", "member"):
        return True
    if st == "restricted":
        return bool(getattr(member, "is_member", True))
    return False


async def alert_owner(client, key: str, text: str):
    now = time.time()
    if now - _ALERTED_AT.get(key, 0) < ALERT_GAP_SEC:
        return
    _ALERTED_AT[key] = now
    log.warning("[ForceSub] " + re.sub(r"<[^>]+>", "", text))
    try:
        await client.send_message(OWNER_ID, f"⚠️ <b>Force Subscribe Alert</b>\n\n{text}")
    except Exception:
        pass  # the owner has not started the bot - ignore


async def _get_member(client, chat_id: int, user_id: int):
    try:
        return await client.get_chat_member(chat_id, user_id)
    except (PeerIdInvalid, ChannelInvalid):
        # the bot has not "seen" this channel yet: resolve it once, then retry
        await client.get_chat(chat_id)
        return await client.get_chat_member(chat_id, user_id)


async def get_join_link(client, ch: dict, user_id: int, fresh: bool = False) -> str:
    key = (ch["chat_id"], user_id)
    cached = _LINK_CACHE.get(key)
    if not fresh and cached and cached[1] > time.time() + 60:
        return cached[0]
    try:
        link = await client.create_chat_invite_link(
            ch["chat_id"],
            name=f"u{user_id}"[:32],
            expire_date=datetime.now() + timedelta(seconds=INVITE_TTL_SEC),
            member_limit=1,
        )
        if len(_LINK_CACHE) > 5000:
            now = time.time()
            for k in [k for k, v in _LINK_CACHE.items() if v[1] < now]:
                _LINK_CACHE.pop(k, None)
        _LINK_CACHE[key] = (link.invite_link, time.time() + INVITE_TTL_SEC)
        return link.invite_link
    except Exception as e:
        await alert_owner(
            client,
            f"invite:{ch['chat_id']}",
            f"Could not create an invite link for <b>{html.escape(ch['title'])}</b> "
            f"(<code>{ch['chat_id']}</code>): {html.escape(str(e))}\n"
            'Make the bot an admin there with the "Invite Users" permission. '
            "Until then the link from config.py is used.",
        )
        return ch["link"]


async def get_missing(client, user_id: int) -> list:
    """Channels this user has NOT joined (also saves / removes the joined records)."""

    async def check(ch):
        try:
            member = await _get_member(client, ch["chat_id"], user_id)
            return ch, _is_in(member), False
        except UserNotParticipant:
            return ch, False, False
        except Exception as e:
            # Config problem (bot not admin / wrong chat_id): skip that channel instead of
            # locking every user out of the bot.
            await alert_owner(
                client,
                f"check:{ch['chat_id']}",
                f"Could not check membership in <b>{html.escape(ch['title'])}</b> "
                f"(<code>{ch['chat_id']}</code>): {html.escape(str(e))}\n"
                "Make the bot an admin in that channel and verify the chat_id. "
                "This channel is skipped until it is fixed.",
            )
            return ch, True, True

    results = await asyncio.gather(*(check(ch) for ch in CHANNELS))
    missing = []
    for ch, joined, failed in results:
        if failed:
            continue
        if joined:
            _LINK_CACHE.pop((ch["chat_id"], user_id), None)
            mark_joined(user_id, ch["chat_id"])
        else:
            unmark(user_id, ch["chat_id"])
            missing.append(ch)
    if not missing:
        _PASSED_AT[user_id] = time.time()
    return missing


def _clean_name(user) -> str:
    name = getattr(user, "first_name", None) or "User"
    return html.escape(re.sub(r"[*_`~|\[\]]", "", name).strip() or "User")


async def build_prompt(client, user, missing: list):
    text = (
        f"<b>HEY {_clean_name(user)}</b>\n\n"
        "<b>JOIN OUR CHANNELS FIRST ‼️ THEN USE THE BOT</b>\n\n"
        "<i>Join all the channels below, then press 🔄 TRY AGAIN.</i>"
    )
    links = await asyncio.gather(*(get_join_link(client, ch, user.id) for ch in missing))
    buttons = [
        InlineKeyboardButton(f"⭐ {ch['title']}", url=url)
        for ch, url in zip(missing, links)
        if url
    ]
    rows = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton("🔄 TRY AGAIN", callback_data="fs_retry")])
    return text, InlineKeyboardMarkup(rows)


async def _send_prompt(client, user, chat_id: int, missing: list):
    now = time.time()
    if now - _PROMPT_AT.get(user.id, 0) < PROMPT_GAP_SEC:
        return
    _PROMPT_AT[user.id] = now
    text, markup = await build_prompt(client, user, missing)
    await client.send_message(
        chat_id, text, reply_markup=markup, disable_web_page_preview=True
    )


# ── GATE: runs before every other handler (group=-2) ──
@UtubeBot.on_message(Filters.private & Filters.incoming, group=-2)
async def fs_gate_message(client: UtubeBot, message: Message):
    user = message.from_user
    if not user or not enabled() or is_exempt(user.id):
        return
    if time.time() - _PASSED_AT.get(user.id, 0) < PASS_CACHE_SEC:
        return
    try:
        missing = await get_missing(client, user.id)
        if not missing:
            return
        await _send_prompt(client, user, message.chat.id, missing)
    except Exception as e:
        log.error(f"[ForceSub] gate error: {e}")
        return  # on an unexpected error never take the whole bot down
    message.stop_propagation()


@UtubeBot.on_callback_query(
    Filters.create(lambda _, __, q: str(q.data) != "fs_retry"), group=-2
)
async def fs_gate_callback(client: UtubeBot, callback_query: CallbackQuery):
    user = callback_query.from_user
    if not user or not enabled() or is_exempt(user.id):
        return
    if time.time() - _PASSED_AT.get(user.id, 0) < PASS_CACHE_SEC:
        return
    try:
        missing = await get_missing(client, user.id)
        if not missing:
            return
        await callback_query.answer("❗ Join all the required channels first.", show_alert=True)
        await _send_prompt(client, user, user.id, missing)
    except Exception as e:
        log.error(f"[ForceSub] callback gate error: {e}")
        return
    callback_query.stop_propagation()


# ── TRY AGAIN button ──
@UtubeBot.on_callback_query(
    Filters.create(lambda _, __, q: str(q.data) == "fs_retry"), group=-2
)
async def fs_retry(client: UtubeBot, callback_query: CallbackQuery):
    user = callback_query.from_user
    missing = []
    if enabled() and not is_exempt(user.id):
        _PASSED_AT.pop(user.id, None)
        missing = await get_missing(client, user.id)

    if missing:
        try:
            await callback_query.answer(
                "❗ Join all the channels first, then press TRY AGAIN.", show_alert=True
            )
            text, markup = await build_prompt(client, user, missing)
            await callback_query.message.edit_text(
                text, reply_markup=markup, disable_web_page_preview=True
            )
        except Exception:
            pass  # e.g. MESSAGE_NOT_MODIFIED
    else:
        try:
            await callback_query.answer("✅ Thanks for joining!")
        except Exception:
            pass
        try:
            await callback_query.message.delete()
        except Exception:
            pass
        try:
            await client.send_message(
                user.id,
                "✅ <b>Thanks for joining!</b>\n\nYou can use the bot now. Send /start to begin.",
            )
        except Exception:
            pass
    callback_query.stop_propagation()


# ── The user left a force-sub channel: DM them right away ──
async def notify_left(client, ch: dict, user_id: int):
    key = (user_id, ch["chat_id"])
    now = time.time()
    if now - _LEFT_DM_AT.get(key, 0) < LEFT_DM_GAP_SEC:
        return
    _LEFT_DM_AT[key] = now
    _PASSED_AT.pop(user_id, None)
    try:
        _LINK_CACHE.pop((ch["chat_id"], user_id), None)
        link = await get_join_link(client, ch, user_id, fresh=True)
        text = (
            f"😡 <b>Dude, why you left from this {html.escape(ch['title'])}?</b>\n\n"
            "Please join it again, otherwise you can't use me."
        )
        markup = (
            InlineKeyboardMarkup([[InlineKeyboardButton(f"✅ Join Now - {ch['title']}", url=link)]])
            if link
            else None
        )
        await client.send_message(
            user_id, text, reply_markup=markup, disable_web_page_preview=True
        )
        log.info(f"[ForceSub] left-DM sent: user {user_id} left {ch['title']}")
    except Exception as e:
        # the user never started the bot or has blocked it - the DM cannot be delivered
        log.info(f"[ForceSub] left-DM skipped: {e}")


# ── Instant detection through Telegram chat member updates ──
# (only registered when this Pyrogram version supports the update; the sweep below
#  is the backup in every case)
_member_updates = getattr(UtubeBot, "on_chat_member_updated", None)

if _member_updates is not None:

    @_member_updates()
    async def fs_member_updated(client: UtubeBot, update):
        try:
            ch = BY_ID.get(update.chat.id) if update.chat else None
            if not ch or not enabled():
                return
            old, new = update.old_chat_member, update.new_chat_member
            member = new or old
            user = getattr(member, "user", None)
            if not user or user.is_bot:
                return

            # User joined: save it
            if _is_in(new):
                _LINK_CACHE.pop((ch["chat_id"], user.id), None)
                if not is_exempt(user.id):
                    mark_joined(user.id, ch["chat_id"])
                return

            # User is no longer in the channel: remove the saved record
            unmark(user.id, ch["chat_id"])

            # DM only for a real "left" (not for ban/kick)
            banned = new is not None and _status(new) == "banned"
            if banned or not _is_in(old) or is_exempt(user.id):
                return
            await notify_left(client, ch, user.id)
        except Exception as e:
            log.error(f"[ForceSub] chat_member error: {e}")


# ── Backup detection: re-check every saved joined user periodically ──
_sweeping = False


async def sweep(client):
    global _sweeping
    if _sweeping or not enabled():
        return
    _sweeping = True
    try:
        n = 0
        for chat_id, uid in saved_records():
            ch = BY_ID.get(chat_id)
            if not ch or is_exempt(uid):
                continue
            try:
                member = await _get_member(client, chat_id, uid)
                joined = _is_in(member)
                banned = _status(member) == "banned"
            except UserNotParticipant:
                joined, banned = False, False
            except Exception:
                continue  # temporary API error - try again in the next sweep
            if not joined:
                unmark(uid, chat_id)
                if not banned:
                    await notify_left(client, ch, uid)
            n += 1
            if n % 20 == 0:
                await asyncio.sleep(1)  # stay under Telegram rate limits
    except Exception as e:
        log.error(f"[ForceSub] sweep error: {e}")
    finally:
        _sweeping = False


_sweeper_started = False


async def _sweep_loop(client):
    while True:
        await asyncio.sleep(SWEEP_SECONDS)
        try:
            await sweep(client)
        except Exception as e:
            log.error(f"[ForceSub] sweep loop error: {e}")


async def _startup_check(client):
    """Is the bot an admin in every force-sub channel?"""
    try:
        me = await client.get_me()
        for ch in CHANNELS:
            try:
                m = await _get_member(client, ch["chat_id"], me.id)
                if _status(m) not in ("administrator", "owner"):
                    await alert_owner(
                        client,
                        f"admin:{ch['chat_id']}",
                        f"The bot is not an admin in <b>{html.escape(ch['title'])}</b> "
                        f"(<code>{ch['chat_id']}</code>). Make it an admin, otherwise membership "
                        "checks and invite links will not work.",
                    )
                else:
                    log.info(f"[ForceSub] OK: {ch['title']} ({ch['chat_id']})")
            except Exception as e:
                await alert_owner(
                    client,
                    f"admin:{ch['chat_id']}",
                    f"Cannot access <b>{html.escape(ch['title'])}</b> (<code>{ch['chat_id']}</code>): "
                    f"{html.escape(str(e))}\nIs the chat_id correct? Is the bot an admin of the channel?",
                )
    except Exception as e:
        log.error(f"[ForceSub] startup check failed: {e}")


def start_background(client):
    """Called once from UtubeBot.start() after the bot has logged in."""
    global _sweeper_started
    if _sweeper_started:
        return
    _sweeper_started = True
    if not FORCE_SUB_ENABLED:
        log.info("[ForceSub] disabled (FORCE_SUB_ENABLED=False)")
        return
    if not CHANNELS:
        log.info("[ForceSub] no valid channel configured - force subscribe is off")
        return
    asyncio.get_event_loop().create_task(_startup_check(client))
    if SWEEP_SECONDS > 0:
        asyncio.get_event_loop().create_task(_sweep_loop(client))
        log.info(f"[ForceSub] leave-sweep every {SWEEP_SECONDS}s")
    log.info(f"[ForceSub] enabled with {len(CHANNELS)} channel(s)")
