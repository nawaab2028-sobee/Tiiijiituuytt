import random

from pyrogram import filters as Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from ..translations import Messages as tr
from ..config import Config
from ..auth_store import auth_filter, add_broadcast_user
from ..utubebot import UtubeBot


@UtubeBot.on_message(
    Filters.private
    & Filters.incoming
    & Filters.command("start")
    & auth_filter
)
async def _start(c: UtubeBot, m: Message):
    add_broadcast_user(m.from_user.id)

    await m.reply_chat_action("typing")
    await m.reply_photo(
        photo=random.choice(tr.IMAGE_LIST),
        caption=tr.START_MSG.format(m.from_user.first_name),
        quote=True,
    )
