import logging

from pyrogram import filters as Filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from ..config import Config
from ..auth_store import add_broadcast_user
from ..plan_utils import myplan_text, premium_text, plan_info
from ..utubebot import UtubeBot


log = logging.getLogger(__name__)


def plan_buttons(user_id: int):
    kind = plan_info(user_id)[0]
    rows = []
    if kind == "free":
        rows.append([InlineKeyboardButton("💎 View Premium Plans", callback_data="premium_plans_btn")])
        rows.append([InlineKeyboardButton("📞 Contact Admin", url=Config.ADMIN_CONTACT_URL)])
    else:
        rows.append([InlineKeyboardButton("💎 Premium Plans", callback_data="premium_plans_btn")])
    return InlineKeyboardMarkup(rows)


def premium_buttons():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💳 Buy Premium Now", url=Config.ADMIN_CONTACT_URL)],
            [InlineKeyboardButton("⬅️ Back to My Plan", callback_data="myplan_back_btn")],
        ]
    )


# group=-1: runs for EVERY user (free or premium) before the free-user catch-all handler
@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("myplan"), group=-1
)
async def _myplan(c: UtubeBot, m: Message):
    add_broadcast_user(m.from_user.id)
    await m.reply_text(
        myplan_text(m.from_user),
        reply_markup=plan_buttons(m.from_user.id),
        disable_web_page_preview=True,
    )
    m.stop_propagation()


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("premium"), group=-1
)
async def _premium(c: UtubeBot, m: Message):
    add_broadcast_user(m.from_user.id)
    await m.reply_text(
        premium_text(),
        reply_markup=premium_buttons(),
        disable_web_page_preview=True,
    )
    m.stop_propagation()


async def _edit_or_reply(q: CallbackQuery, text: str, markup):
    try:
        await q.edit_message_text(text, reply_markup=markup, disable_web_page_preview=True)
    except Exception:
        # e.g. the button sits on a photo message (/start welcome) - send a new message instead
        try:
            await q.message.reply_text(text, reply_markup=markup, disable_web_page_preview=True)
        except Exception as e:
            log.info(e)


@UtubeBot.on_callback_query(
    Filters.create(lambda _, __, q: str(q.data) == "premium_plans_btn")
)
async def _premium_cb(c: UtubeBot, q: CallbackQuery):
    await q.answer()
    await _edit_or_reply(q, premium_text(), premium_buttons())


@UtubeBot.on_callback_query(
    Filters.create(lambda _, __, q: str(q.data) == "myplan_back_btn")
)
async def _myplan_back_cb(c: UtubeBot, q: CallbackQuery):
    await q.answer()
    await _edit_or_reply(q, myplan_text(q.from_user), plan_buttons(q.from_user.id))
