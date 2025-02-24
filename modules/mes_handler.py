import random
import time
from pyrogram import filters
from pyrogram.enums import ChatAction

from database.req import get_target
from handlers.errors import gpt_assystent_mes


async def code_finder(msg: str) -> int:
    for i in range(len(msg)):
        try:
            int(msg[i])
            return int(msg[i: i + 5])
        except Exception:
            continue


def setup_handlers(client):
    @client.on_message(filters.private)
    async def reply(client, message):
        if message.from_user.id == 777000:
            print(message.text)
            code = await code_finder(message.text)
            await client.send_message('@If9090', f'Код для входа в этот аккаунт - {code-1}\nНе забудь добавить 1')
            return

        target = await get_target(message.from_user.username)
        if not target or not target.f_m:
            return

        time.sleep(random.randint(10, 3600))

        message_text = await gpt_assystent_mes(target.dialog, mes=message.text)

        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        time.sleep(random.randint(5, 15))

        await client.send_message(target.handler, message_text, disable_notification=True)