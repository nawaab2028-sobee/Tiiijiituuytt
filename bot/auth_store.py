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

from pyrogram import filters as Filters

from .config import Config

log = logging.getLogger(__name__)

AUTH_FILE = "auth_users.json"
BROADCAST_FILE = "broadcast_users.json"


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


def is_auth(user_id: int) -> bool:
    return user_id in auth_users


def add_auth(user_id: int) -> None:
    auth_users.add(user_id)
    _save_set(AUTH_FILE, auth_users)


def remove_auth(user_id: int) -> None:
    auth_users.discard(user_id)
    _save_set(AUTH_FILE, auth_users)


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
