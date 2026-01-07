from dotenv import load_dotenv
import os
import asyncio
import src.bot as gryt

load_dotenv()

api_session: str = os.environ["TG_SESSION"]
api_id: int = int(os.environ["TG_API_ID"])
api_hash: str = os.environ["TG_API_HASH"]
api_token: str = os.environ["TG_TOKEN"]

bot = gryt.Bot(api_session, api_id, api_hash)

asyncio.run(bot.run(api_token))
