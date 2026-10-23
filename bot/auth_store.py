"""
Central store for:
  - Authorised users (who can use the bot's upload features)
  - Broadcast users (everyone who has ever pressed /start, auth or not)

Both are JSON-file backed so they survive bot restarts / redeploys, and both
start out pre-loaded with Config.AUTH_USERS (hardcoded / env based list) so
existing behaviour keeps working exactly as before.
"""

import json
import logging
from datetime import datetime, timedelta, timezone

from pyrogram import filters as Filters

from .config import Config

log = logging.getLogger(__name__)

AUTH_FILE = "auth_users.json"
BROADCAST_FILE = "broadcast_users.json"
AUTH_META_FILE = "auth_meta.json"   # per user: when the access started / when it ends


def _load_set(path: str) -> set:
    try:
        with open(path, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def _save_set(path: str, data: set) -> None:
    try:
        with open(path, "w") as f:
            json.dump(list(data), f)
    except Exception as e:
        log.error(f"Failed saving {path}: {e}")


# In-memory sets, pre-seeded with Config.AUTH_USERS so nothing changes for
# users already hardcoded/env-configured. /addauth and /rmauth mutate these
# sets directly (and persist to disk), so the change is instant, no restart
# needed, and survives redeploys via the JSON files.
auth_users: set = _load_set(AUTH_FILE) | set(Config.AUTH_USERS)
broadcast_users: set = _load_set(BROADCAST_FILE)


def _load_meta() -> dict:
    try:
        with open(AUTH_META_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_meta() -> None:
    try:
        with open(AUTH_META_FILE, "w") as f:
            json.dump(auth_meta, f)
    except Exception as e:
        log.error(f"Failed saving {AUTH_META_FILE}: {e}")


# {"<user_id>": {"start": iso-utc, "expiry": iso-utc | None}}
# A user in auth_users without an entry here has permanent access (old behaviour).
auth_meta: dict = _load_meta()


def _parse(value):
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def is_auth(user_id: int) -> bool:
    if user_id not in auth_users:
        return False
    meta = auth_meta.get(str(user_id))
    expiry = _parse(meta.get("expiry")) if meta else None
    if expiry is not None and datetime.now(timezone.utc) >= expiry:
        # the time-limited access has ended -> remove it automatically
        auth_users.discard(user_id)
        auth_meta.pop(str(user_id), None)
        _save_set(AUTH_FILE, auth_users)
        _save_meta()
        return False
    return True


def add_auth(user_id: int, days: int = 0) -> None:
    """days > 0 = access for that many days, days == 0 = permanent."""
    now = datetime.now(timezone.utc)
    auth_users.add(user_id)
    auth_meta[str(user_id)] = {
        "start": now.isoformat(),
        "expiry": (now + timedelta(days=days)).isoformat() if days and days > 0 else None,
    }
    _save_set(AUTH_FILE, auth_users)
    _save_meta()


def remove_auth(user_id: int) -> None:
    auth_users.discard(user_id)
    auth_meta.pop(str(user_id), None)
    _save_set(AUTH_FILE, auth_users)
    _save_meta()


def get_auth_info(user_id: int):
    """(start, expiry) as aware UTC datetimes; either can be None."""
    meta = auth_meta.get(str(user_id)) or {}
    return _parse(meta.get("start")), _parse(meta.get("expiry"))


def get_auth_users() -> set:
    return auth_users


def add_broadcast_user(user_id: int) -> None:
    broadcast_users.add(user_id)
    _save_set(BROADCAST_FILE, broadcast_users)


def get_broadcast_users() -> set:
    return broadcast_users


# Dynamic replacement for `Filters.user(Config.AUTH_USERS)`. The built-in
# Filters.user() bakes a fixed snapshot of the id list at decoration time, so
# it would never see /addauth or /rmauth updates. This filter instead checks
# the live auth_users set on every message.
auth_filter = Filters.create(lambda _, __, m: is_auth(m.from_user.id) if m.from_user else False)

# Same idea, but for the "NOT authorised" case used by non-auth-user.py.
non_auth_filter = Filters.create(lambda _, __, m: not is_auth(m.from_user.id) if m.from_user else False)
