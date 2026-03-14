from dotenv import load_dotenv
import os
from src.bot_config import BotConfig

load_dotenv()

config = BotConfig()

config.session_name = os.environ["TG_SESSION"]
config.api_id = int(os.environ["TG_API_ID"])
config.api_hash = os.environ["TG_API_HASH"]
config.api_token = os.environ["TG_TOKEN"]
config.admin_ids = [int(os.environ["ADMIN_1_ID"]), int(os.environ["ADMIN_2_ID"])]
config.logging_chat_id = int(os.environ["LOG_CHAT_ID"])
config.logging_chat_auth = int(os.environ["LOG_CHAT_AUTH"])

BOT_CONFIG = config
MEDIA_PROXY = os.environ["MEDIA_PROXY"]
YOUTUBE_COOKIES = os.environ["YOUTUBE_COOKIES"]
