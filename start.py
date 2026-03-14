import asyncio
from src.bot import Bot
from src.enviroment import BOT_CONFIG

bot = Bot(BOT_CONFIG)

asyncio.run(bot.run())
