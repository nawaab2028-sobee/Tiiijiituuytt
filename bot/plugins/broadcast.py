import asyncio
import logging

from pyrogram import filters as Filters
from pyrogram.types import Message

from ..utubebot import UtubeBot
from ..config import Config
from ..auth_store import get_broadcast_users


log = logging.getLogger(__name__)

owner_filter = Filters.create(lambda _, __, m: bool(m.from_user) and m.from_user.id == Config.OWNER_ID)


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("broadcast") & owner_filter
)
async def _broadcast(c: UtubeBot, m: Message):
    if not m.reply_to_message:
        await m.reply_text("📢 Reply to a message to broadcast it.", True)
        return

    users = get_broadcast_users()
    total = len(users)
    if total == 0:
        await m.reply_text("No users to broadcast to yet.", True)
        return

    status = await m.reply_text(f"📢 Broadcasting to {total} user(s)...", True)
    success, failed = 0, 0
    for uid in list(users):
        try:
            await m.reply_to_message.copy(uid)
            success += 1
            await asyncio.sleep(0.05)  # flood prevention
        except Exception as e:
            failed += 1
            log.debug(f"Broadcast failed for {uid}: {e}")

    await status.edit_text(
        f"📢 **Broadcast complete!**\n\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"👥 Total: {total}"
    )


@UtubeBot.on_message(
    Filters.private & Filters.incoming & Filters.command("broadusers") & owner_filter
)
async def _broadusers(c: UtubeBot, m: Message):
    users = list(get_broadcast_users())
    total = len(users)
    if total == 0:
        await m.reply_text("📋 No broadcast users registered yet.", True)
        return
    uid_list = "\n".join(f"• `{uid}`" for uid in users[:50])
    suffix = f"\n\n...and {total - 50} more." if total > 50 else ""
    await m.reply_text(f"👥 **Broadcast users ({total}):**\n\n{uid_list}{suffix}", True)
