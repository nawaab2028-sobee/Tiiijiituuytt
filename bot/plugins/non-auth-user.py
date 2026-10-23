import logging
import random
import time

from pyrogram import filters as Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ..utubebot import UtubeBot
from ..config import Config
from ..translations import Messages as tr
from ..auth_store import non_auth_filter, add_broadcast_user
from ..plan_utils import free_start_caption, FREE_NOTICE


log = logging.getLogger(__name__)

_NOTICE_AT = {}
NOTICE_GAP_SEC = 5


def _free_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💎 View Premium Plans", callback_data="premium_plans_btn")],
            [InlineKeyboardButton("📞 Contact Admin", url=Config.ADMIN_CONTACT_URL)],
        ]
    )


def _command_of(m: Message) -> str:
    text = (m.text or m.caption or "").strip()
    if not text.startswith("/"):
        return ""
    return text.split()[0][1:].split("@")[0].lower()


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & non_auth_filter
    & ~Filters.command(["myplan", "premium"])
)
async def _non_auth_usr_msg(c: UtubeBot, m: Message):
    add_broadcast_user(m.from_user.id)
    cmd = _command_of(m)

    # Free user pressed /start (or /help): ALWAYS answer with the image + caption.
    # (The message is not deleted first, so nothing can break the reply.)
    if cmd in ("start", "help"):
        await m.reply_chat_action("typing")
        await m.reply_photo(
            photo=random.choice(tr.IMAGE_LIST),
            caption=free_start_caption(m.from_user),
            reply_markup=_free_buttons(),
        )
        return

    # Any other message / command from a free user: tell them what is going on
    # (once every few seconds), then clean their message up like before.
    now = time.time()
    if now - _NOTICE_AT.get(m.from_user.id, 0) >= NOTICE_GAP_SEC:
        _NOTICE_AT[m.from_user.id] = now
        try:
            await m.reply_text(FREE_NOTICE, reply_markup=_free_buttons(), quote=False)
        except Exception as e:
            log.info(f"Free user notice failed: {e}")

    try:
        await m.delete(True)
    except Exception as e:
        log.info(f"Could not delete message of unauthorised user {m.from_user.id}: {e}")
    log.info(f"Unauthorised user {m.chat.id} contacted. Message deleted!!")
