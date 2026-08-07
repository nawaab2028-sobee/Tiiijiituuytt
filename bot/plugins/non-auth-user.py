import logging

from pyrogram import filters as Filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..config import Config
from ..translations import Messages as tr
from ..auth_store import non_auth_filter, add_broadcast_user


log = logging.getLogger(__name__)


@UtubeBot.on_message(
    Filters.private & Filters.incoming & non_auth_filter
)
async def _non_auth_usr_msg(c: UtubeBot, m: Message):
    add_broadcast_user(m.from_user.id)
    await m.delete(True)
    log.info(f"Unauthorised user {m.chat} contacted. Message {m} deleted!!")

    if m.command and m.command[0].lower() in ("start", "help"):
        await m.reply_chat_action("typing")
        await m.reply_text(text=tr.NON_AUTH_START_MSG, quote=True)
