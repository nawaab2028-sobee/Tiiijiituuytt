import os

class Config:

    BOT_TOKEN = os.environ.get(
        "BOT_TOKEN", " "
    )

    SESSION_NAME = os.environ.get("SESSION_NAME", "")

    API_ID = int(os.environ.get("API_ID", "22518279"))

    API_HASH = os.environ.get("API_HASH", "61e5cc94bc5e6318643707054e54caf4")

    CLIENT_ID = os.environ.get(
        "CLIENT_ID",
        "235875301142-mg0732tsdmvjt07oi791kf8rtgior5le.apps.googleusercontent.com",
    )

    CLIENT_SECRET = os.environ.get(
        "CLIENT_SECRET", "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"
    )

    # Owner is allowed to use /addauth, /rmauth, /users, /broadcast, /broadusers
    OWNER_ID = int(os.environ.get("OWNER_ID", "8909902924"))

    _AUTH_USERS_DEFAULT = (
        "8845596819,7988815969,8680968748,8429278856,8723278238,8313091010,8902042822,8480660521,8971045439,"
        "8838086114"
    )
    AUTH_USERS = [
        int(uid)
        for uid in os.environ.get("AUTH_USERS", _AUTH_USERS_DEFAULT).split(",")
        if uid.strip()
    ]
    if OWNER_ID not in AUTH_USERS:
        AUTH_USERS.append(OWNER_ID)

    VIDEO_DESCRIPTION = os.environ.get(
        "VIDEO_DESCRIPTION",
        "Uploaded By Smarty Brother. Only For Education Purpose!",
    )

    VIDEO_CATEGORY = os.environ.get("VIDEO_CATEGORY", "")

    VIDEO_TITLE_PREFIX = os.environ.get("VIDEO_TITLE_PREFIX", "")

    VIDEO_TITLE_SUFFIX = os.environ.get("VIDEO_TITLE_SUFFIX", "—MS Bro")

    DEBUG = bool(os.environ.get("DEBUG", ""))

    UPLOAD_MODE = os.environ.get("UPLOAD_MODE", "unlisted")

    CRED_FILE = os.environ.get("CRED_FILE", "auth_token.txt")

    # ─── Force Subscribe ──────────────────────────────────────────────────────
    # True  = every user must join ALL the channels below before using the bot
    # False = force subscribe is off
    FORCE_SUB_ENABLED = os.environ.get("FORCE_SUB_ENABLED", "True").lower() == "true"

    # True = the owner does not have to join
    FORCE_SUB_EXEMPT_OWNER = os.environ.get("FORCE_SUB_EXEMPT_OWNER", "True").lower() == "true"

    # Every N seconds the bot re-checks saved members to catch users who left a
    # channel (backup for the instant leave detection). 0 = off.
    FORCE_SUB_SWEEP_SECONDS = int(os.environ.get("FORCE_SUB_SWEEP_SECONDS", "60"))

    # Every channel has 3 fields:
    #   title   -> name shown on the button / in messages
    #   link    -> channel link (fallback, the bot also creates personal invite links)
    #   chat_id -> channel id (the "-100..." one). The bot must be ADMIN in that channel.
    # A channel whose chat_id is still the "-100XXXXXXXXXX" placeholder is ignored.
    FORCE_SUB_CHANNELS = [
        {"title": "Channel 1", "link": "https://t.me/your_channel_1", "chat_id": "-100XXXXXXXXXX"},
        {"title": "Channel 2", "link": "https://t.me/your_channel_2", "chat_id": "-100XXXXXXXXXX"},
    ]

    # Where users contact the owner to buy Premium
    ADMIN_CONTACT_URL = os.environ.get("ADMIN_CONTACT_URL", "https://t.me/SmartBoy_ApnaMS")

    # "How to Login??" button on /login
    LOGIN_GUIDE_URL = os.environ.get("LOGIN_GUIDE_URL", "https://t.me/TGtoYt_Guidance/5")
