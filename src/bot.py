import telethon
from telethon import events
from telethon.events import NewMessage, filters
from telethon.types import ChannelRef, User #, UserRef, GroupRef

import html
from typing import Any, cast
import asyncio
import signal
import re

from src.sites.youtube_media import YouTubeMediaAPI
import src.sites.site_base as site_base
from src.logger import LOGFILE_PATH, logger
import src.translations as s
from src.user_settings import UserSettings

sites_APIs: list[site_base.SiteAPI] = [] # [YouTubeDashAPI, YandexMusicAPI, DzenDashAPI]

YouTubeMediaAPI.get_data("https://youtu.be/7pbcW63C6yw?si=jeGQrfioU0p_xkXY")
exit()

class BotConfig:
    session_name: str
    api_id: int
    api_hash: str
    api_token: str
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
            session=self.config.session_name,
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
        )

        # Setup message handlers
        @self.client.on(events.NewMessage, filters.Command('/start'))
        async def command_start_handler(event: Any) -> None:
            msg = cast(NewMessage, event)
            logger.info(f"{html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")}: {msg.text}")
            await on_command_start(self, msg)

        @self.client.on(events.NewMessage, filters.Command('/logs'))
        async def command_logs_handler(event: Any) -> None:
            msg = cast(NewMessage, event)
            logger.info(f"{html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")}: {msg.text}")
            await on_command_logs(self, msg)

        @self.client.on(events.NewMessage, filters.All(filters.ChatType(User), filters.Incoming()))
        async def new_text_message(event: Any) -> None:
            msg = cast(NewMessage, event)
            logger.info(f"{html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")}: {msg.text}")
            await on_new_text_message(self, msg)

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


async def on_command_start(bot: Bot, msg: NewMessage) -> None:
    name = html.escape(s=msg.chat.name or msg.chat.username or str(msg.chat.id) or '')
    await msg.respond(markdown=f"Hello, **{name}**!")

async def on_command_logs(bot: Bot, msg: NewMessage) -> None:
    if msg.chat.id in bot.config.admin_ids or msg.chat.id == bot.config.logging_chat_id:
        await bot.client.send_file(msg.chat, file=LOGFILE_PATH)
    else:
        await msg.respond("You have no permissions.")

async def on_new_text_message(bot: Bot, msg: NewMessage) -> None:
    # Обновление статуса пользователя в БД (позже)
    user_settings = get_user_settings(bot, msg.chat.id)
    lang = user_settings.default_language

    # Filter msg.text
    if not msg.text:
        await msg.reply(s.err_message_empty[lang])
        return
    if msg.text.startswith("/"):
        await msg.reply(s.err_unknown_command[lang])
        return

    link, site_API, error_message = parse_user_input(msg.text)

    if error_message:
        await msg.reply(error_message[lang])
        return


    # Получение данных (с прогрессом, так как проверка каждой впн и акка занимает время)
    # Создание клавиатуры кнопок по данным
    # Отправка сообщения с картинкой
    # Создание request в бд (позже)
    # И сохранение его в оперативке
    pass

def get_user_settings(bot: Bot, telegram_user_id: int) -> UserSettings:
    """
    try:
        user_settings_data = bot.database.get_user_settings(telegram_user_id)

        user_settings = UserSettings()
        user_settings.telegram_user_id = telegram_user_id
        user_settings.default_language = user_settings_data["default_language"]
        user_settings.default_audio_caption = user_settings_data["default_audio_caption"]
        user_settings.default_video_caption = user_settings_data["default_video_caption"]
        user_settings.default_post_caption = user_settings_data["default_post_caption"]
        user_settings.default_share_status = user_settings_data["default_share_status"]
        user_settings.allow_press_buttons = user_settings_data["allow_press_buttons"]

        return user_settings
    except:
        bot.database.reconnect()
    """
    return UserSettings()

def is_link(link: str) -> bool:
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # ...localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return (re.match(regex, link) is not None)

def parse_user_input(input: str) -> tuple[str, site_base.SiteAPI, dict]: # [link, siteAPI, error_message]
    input = input.lstrip()
    splitted = input.split(maxsplit=1)

    if len(splitted) == 0:
        return "", site_base.SiteAPI(), s.err_message_empty

    link = splitted[0]

    if not is_link(link):
        return "", site_base.SiteAPI(), s.err_not_link

    for site_API in sites_APIs:
        if site_API.supports(link):
            return link, site_API, dict()

    return link, site_base.SiteAPI(), s.err_no_link_support
