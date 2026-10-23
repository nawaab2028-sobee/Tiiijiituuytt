from pyrogram import Client

from .config import Config


class UtubeBot(Client):
    def __init__(self):
        super().__init__(
            session_name=Config.SESSION_NAME,
            bot_token=Config.BOT_TOKEN,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            plugins=dict(root="bot.plugins"),
            workers=15,
        )
        self.DOWNLOAD_WORKERS = 15
        self.counter = 0
        self.download_controller = {}

    async def start(self):
        await super().start()
        # Force Subscribe: start the "user left a channel" sweep (never blocks startup)
        try:
            from .plugins import forcesub

            forcesub.start_background(self)
        except Exception as e:
            import logging

            logging.getLogger(__name__).error(f"[ForceSub] background start failed: {e}")
        return self
