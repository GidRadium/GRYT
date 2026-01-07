import telethon
from telethon import events
from telethon.events import NewMessage, filters
import html
from typing import Any, cast

import logging
logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)


async def command_start_handler(event: Any):
    msg = cast(NewMessage, event)
    sender = html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")
    print(f"{sender}: {msg.text}")

    name = html.escape(s=msg.chat.name or msg.chat.username or str(msg.chat.id) or '')

    await msg.respond(markdown=f"Hello, **{name}**!")

async def my_print_handler(event):
    msg = cast(NewMessage, event)
    sender = html.escape(s=f"[{msg.chat.id}] {(msg.chat.name or msg.chat.username or '')}")
    print(f"{sender}: {msg.text}")

class Bot:
    client: telethon.Client
    def __init__(self, session_name: str, api_id: int, api_hash: str):
        self.session = session_name
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = telethon.Client(
            session=session_name,
            api_id=api_id,
            api_hash=api_hash,
        )
        # self.client.add_event_handler(command_start_handler, events.NewMessage, filters.Command('/start'))
        self.client.add_event_handler(
            command_start_handler,
            events.NewMessage,
            filters.Command('/start')
        )
        self.client.add_event_handler(my_print_handler, events.NewMessage)

    async def run(self, api_token: str):
        await self.client.connect()
        await self.client.interactive_login(phone_or_token=api_token)
        print("Bot started!")
        await self.client.run_until_disconnected()
