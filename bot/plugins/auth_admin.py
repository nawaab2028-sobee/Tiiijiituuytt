import logging

from pyrogram import filters as Filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..config import Config
from ..auth_store import add_auth, remove_auth, get_auth_users


log = logging.getLogger(__name__)

owner_filter = Filters.create(lambda _, __, m: bool(m.from_user) and m.from_user.id == Config.OWNER_ID)


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("addauth") & owner_filter
)
async def _addauth(c: UtubeBot, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Usage: /addauth user_id", True)
        return
    try:
        uid = int(m.command[1])
    except ValueError:
        await m.reply_text("Invalid user id.", True)
        return

    add_auth(uid)
    await m.reply_text(
        f"✅ User `{uid}` added to authorised list.\nNow this user can use this bot.",
        True,
    )


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("rmauth") & owner_filter
)
async def _rmauth(c: UtubeBot, m: Message):
    if len(m.command) < 2:
        await m.reply_text("Usage: /rmauth user_id", True)
        return
    try:
        uid = int(m.command[1])
    except ValueError:
        await m.reply_text("Invalid user id.", True)
        return

    remove_auth(uid)
    await m.reply_text(
        f"✅ User `{uid}` removed from authorised list.\nNow this user can't use this bot.",
        True,
    )


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("users") & owner_filter
)
async def _users(c: UtubeBot, m: Message):
    users = get_auth_users()
    if not users:
        await m.reply_text("📋 No authorised users yet.", True)
        return
    user_list = "\n".join(f"• `{uid}`" for uid in users)
    await m.reply_text(f"👥 **Authorised users ({len(users)}):**\n\n{user_list}", True)
