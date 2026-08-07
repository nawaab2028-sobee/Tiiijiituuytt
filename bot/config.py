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
