import asyncio
import random
import time
from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.errors import InviteRequestSent, InviteHashExpired, UserAlreadyParticipant

from database.req import get_target, update_target, get_all_bots_names
from handlers.errors import gpt_assystent_mes
from instance import logger, links, messages
from modules.scheduler import schedule_follow_ups, schedule_delete_chat, cancel_follow_ups

pending_replies = {}


async def code_finder(msg: str) -> int:
    for i in range(len(msg)):
        try:
            int(msg[i])
            return int(msg[i: i + 5])
        except Exception:
            continue


async def join_chat(client, chat_link: str) -> str:
    if not chat_link.startswith('https://t.me/+'):
        chat_link = chat_link.replace('https://t.me/', '')
    try:
        chat = await client.join_chat(chat_link)
        logger.info(f"Успешно присоединилися к чату {chat.title}")
        return "good"
    except UserAlreadyParticipant:
        logger.info("Клиент уже состоит в этом чате.")
        return "good"
    except InviteRequestSent:
        logger.info("Запрос на присоединение отправлен и ожидает одобрения администратора.")
        return "Запрос на присоединение отправлен и ожидает одобрения администратора."
    except InviteHashExpired:
        logger.info("Ссылка приглашения недействительна или истекла.")
        return "Ссылка приглашения недействительна или истекла."
    except Exception as e:
        logger.info(f"Произошла ошибка: {e}")
        return "Произошла неизветсная ошибка. Можете добавить бота самостоятельно."


async def get_ans() -> str:
    prob = random.randint(1, 70)
    if prob == 7:
        return random.choice(links)
    return random.choice(messages)


def setup_handlers(client):
    @client.on_message(filters.private)
    async def reply(client, message):
        brothers = await get_all_bots_names()
        if message.from_user.id in brothers:
            await asyncio.sleep(random.randint(1800, 6000))
            message_text = message.text.lower()
            if message_text.startswith("@"):
                message_text = message_text.replace("@", "https://t.me/")
                res = await join_chat(client, message_text)
                if res != 'good':
                    await client.send_message('@If9090', res)
            ans = await get_ans()
            await client.send_message(message.from_user.id, ans)
            return
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
        cancel_follow_ups(target.handler)
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

        schedule_follow_ups(client, target.handler)
        schedule_delete_chat(client, target.handler)
