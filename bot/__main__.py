import logging
import os
import threading
import time

from flask import Flask
from pyrogram.errors import BadMsgNotification

from .utubebot import UtubeBot
from .config import Config


# ─── Flask keep-alive server for Render ───────────────────────────────────────

flask_app = Flask(__name__)


@flask_app.route("/")
def index():
    return "Bot is running!"


def run_flask():
    port = int(os.environ.get("PORT", 8000))
    flask_app.run(host="0.0.0.0", port=port)


# Start Flask in background thread so Render detects open port
threading.Thread(target=run_flask, daemon=True).start()

# ──────────────────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG if Config.DEBUG else logging.INFO)
    logging.getLogger("pyrogram").setLevel(
        logging.INFO if Config.DEBUG else logging.WARNING
    )

    log = logging.getLogger(__name__)

    # Retry startup on BadMsgNotification [16] ("client time has to be
    # synchronized"). This error happens when the container's system clock
    # is out of sync with Telegram's servers on the first connection attempt.
    # A short wait + retry lets the clock/session settle instead of crashing.
    MAX_START_RETRIES = 5
    RETRY_DELAY_SECONDS = 5

    for attempt in range(1, MAX_START_RETRIES + 1):
        try:
            UtubeBot().run()
            break
        except BadMsgNotification as e:
            log.warning(
                "Startup attempt %s/%s failed due to clock sync issue: %s",
                attempt,
                MAX_START_RETRIES,
                e,
            )
            if attempt == MAX_START_RETRIES:
                log.error(
                    "Bot could not start after %s attempts due to persistent "
                    "clock sync issues. Check that the server/container time "
                    "is correct.",
                    MAX_START_RETRIES,
                )
                raise
            time.sleep(RETRY_DELAY_SECONDS)
