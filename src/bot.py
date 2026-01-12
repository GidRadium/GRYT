import telethon
from telethon import events
from telethon.events import NewMessage, filters
from telethon.types import ChannelRef #, UserRef, GroupRef
import html
from typing import Any, cast
import asyncio
import signal

from src.logger import LOGFILE_PATH, logger

class BotConfig:
    session_name: str
    api_id: int
    api_hash: str
    api_token: str
    cache_chat_id: int
    logging_chat_id: int
    logging_chat_auth: int
    admin_ids: list[int]


class Bot:
    client: telethon.Client
    config: BotConfig
    _shutting_down = False

    def __init__(self, config: BotConfig):
        self.config = config

        # Create telethon client
        self.client = telethon.Client(
            session=config.session_name,
            api_id=config.api_id,
            api_hash=config.api_hash,
        )

        # Setup message handlers
        @self.client.on(events.NewMessage, filters.Command('/start'))
        async def command_start_handler(event: Any) -> None:
            msg = cast(NewMessage, event)
            sender = html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")
            logger.info(f"{sender}: {msg.text}")

            name = html.escape(s=msg.chat.name or msg.chat.username or str(msg.chat.id) or '')
            await msg.respond(markdown=f"Hello, **{name}**!")

        @self.client.on(events.NewMessage, filters.Command('/logs'))
        async def command_logs_handler(event: Any) -> None:
            msg = cast(NewMessage, event)
            sender = html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")
            logger.info(f"{sender}: {msg.text}")

            if msg.chat.id in self.config.admin_ids or msg.chat.id == self.config.logging_chat_id:
                await self.client.send_file(msg.chat, file=LOGFILE_PATH)
            else:
                await msg.respond("You have no permissions.")

        @self.client.on(events.NewMessage)
        async def my_print_handler(event: Any) -> None:
            msg = cast(NewMessage, event)
            sender = html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")
            logger.info(f"{sender}: {msg.text}")

    async def shutdown(self):
            if self._shutting_down:
                return
            self._shutting_down = True

            logger.info("Stopping bot...")

            try:
                await self.client.send_message(
                    ChannelRef(self.config.logging_chat_id, self.config.logging_chat_auth),
                    "Bot stopped."
                )
            except Exception as e:
                logger.exception(msg="Can't send stopping message.", exc_info=e)

            await self.client.disconnect()


    async def run(self):
        # Register Ctrl+C
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.shutdown()))

        # Start bot
        logger.info("Connecting to telegram.")
        await self.client.connect()
        logger.info("Starting bot.")
        await self.client.interactive_login(phone_or_token=self.config.api_token)
        logger.info("Bot started!")
        try:
            await self.client.send_message(
                ChannelRef(self.config.logging_chat_id, self.config.logging_chat_auth),
                "Bot started!"
            )
        except Exception as e:
            logger.exception(msg="Can't send starting message.", exc_info=e)
        await self.client.run_until_disconnected()
        logger.info("Bot stopped.")
