"""
Plan helpers: IST time formatting, the Free / Premium texts and the premium
pricing (same plans as the Save Restriction bot).
"""

import html
import os
import re
from datetime import datetime, timedelta, timezone

from .config import Config
from .auth_store import is_auth, get_auth_info

IST = timezone(timedelta(hours=5, minutes=30))


def to_ist(dt):
    return dt.astimezone(IST) if dt else None


def fmt_ist(dt) -> str:
    return to_ist(dt).strftime("%d %b %Y, %I:%M %p") + " IST"


def fmt_left(delta) -> str:
    secs = max(0, int(delta.total_seconds()))
    days, rem = divmod(secs, 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    return f"{days}d {hours}h {minutes}m"


def safe_name(user) -> str:
    """HTML safe first name (markdown characters removed, the parser mixes both)."""
    name = (getattr(user, "first_name", None) or "User")
    name = re.sub(r"[*_`~|\[\]]", "", name).strip() or "User"
    return html.escape(name)


def mention(user) -> str:
    return f'<a href="tg://user?id={user.id}">{safe_name(user)}</a>'


PREMIUM_BENEFITS = (
    "<b>Why Go Premium?</b>\n"
    "• 🚀 Upload Telegram videos to YouTube\n"
    "• 🔑 Login with your own YouTube account\n"
    "• ⚡ Fast download and upload\n"
    "• 🔗 YouTube link sent right after the upload\n"
    "• 👑 Premium badge"
)

PREMIUM_PRICING = (
    "<b>💲 Pricing:</b>\n"
    "• <b>1 Week Plan:</b> ₹50 / $0.5\n"
    "• <b>1 Month Plan:</b> ₹150/ $1.5 (Save 25%)\n"
    "• <b>3 Month Plan:</b> ₹300 / $3 (save 50%)"
)


def premium_text() -> str:
    return (
        "<b>💎 Premium Plans</b>\n\n"
        f"{PREMIUM_BENEFITS}\n\n"
        f"{PREMIUM_PRICING}\n\n"
        "<i>Tap the button below to buy. After payment send the screenshot to the "
        "owner for instant activation.</i>"
    )


def free_start_caption(user) -> str:
    return (
        f"<b>Hey {mention(user)} 👋</b>\n\n"
        "<b>I'm Advanced YouTube Uploader Bot.</b>\n"
        "<b>👤 Your Plan: Free</b>\n"
        "🔒 Uploading is locked for Free plan users. Get Premium to unlock it.\n\n"
        "<b>⚙️ How it works:</b>\n"
        "1️⃣ Buy Premium from the owner\n"
        "2️⃣ Send /login and authorise your YouTube account\n"
        "3️⃣ Forward any Telegram video to me\n"
        "4️⃣ Reply /upload (optional title) to that video\n"
        "5️⃣ I download it, upload it and send you the YouTube link\n\n"
        f"{PREMIUM_PRICING}\n\n"
        "Send /myplan to see your plan, /premium for all the details."
    )


FREE_NOTICE = (
    "<b>🔒 This feature is only for Premium users.</b>\n\n"
    "You are on the <b>Free</b> plan. Send /premium to see the plans or /myplan to "
    "check your plan."
    "Contact: @SmartBoy_ApnaMS ."
)


def plan_info(user_id: int):
    """('owner'|'premium'|'free', start, expiry)"""
    if user_id == Config.OWNER_ID:
        return "owner", None, None
    if is_auth(user_id):
        start, expiry = get_auth_info(user_id)
        return "premium", start, expiry
    return "free", None, None


def myplan_text(user) -> str:
    kind, start, expiry = plan_info(user.id)
    linked = "✅ Yes" if os.path.exists(Config.CRED_FILE) else "❌ Not yet (use /login)"
    head = (
        f"<b>👤 Name:</b> {safe_name(user)}\n"
        f"<b>🆔 User ID:</b> <code>{user.id}</code>\n\n"
    )

    if kind == "owner":
        body = (
            "<b>👑 Plan: Owner</b>\n\n"
            "<b>📅 Validity:</b> <code>Lifetime (Owner)</code>\n\n"
            "<b>🚀 YouTube Uploads:</b> Unlocked\n"
        )
    elif kind == "premium":
        start_text = fmt_ist(start) if start else "Not recorded"
        if expiry is None:
            end_text = "Lifetime (Permanent)"
            left = ""
        else:
            end_text = fmt_ist(expiry)
            left = f"<b>⌛ Time Left:</b> <code>{fmt_left(expiry - datetime.now(timezone.utc))}</code>\n"
        body = (
            "<b>👑 Premium Status: Active</b>\n\n"
            f"<b>🟢 Activated From:</b> <code>{start_text}</code>\n"
            f"<b>📅 Valid Till:</b> <code>{end_text}</code>\n"
            f"{left}\n"
            "<b>🚀 YouTube Uploads:</b> ✅ Unlocked \n"
        )
    else:
        body = (
            "<b>👤 Plan: Free Tier</b>\n\n"
            "<b>🚀 YouTube Uploads:</b> 🔒 Locked\n"
            "<i>Upgrade to Premium to unlock uploading! 🚀</i>\n"
        )

    if kind in ("owner", "premium"):
        body += f"<b>🔗 YouTube Account Linked:</b> {linked}\n\n<i>Thank you for supporting the bot! 🎉</i>"
    return head + body
