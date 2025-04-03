import asyncio
import random
import datetime

from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, UsernameNotModified

from database.req import get_all_targets, update_target, get_bot_status
from handlers.errors import gpt_assystent_mes, create_thread, bots_error_handler
from instance import client
from modules.scheduler import schedule_follow_ups, schedule_delete_chat


mes = """
Привет! Видел ты ищешь заказы в чатах в телеграме.\n
Я недавно тоже начал искать клиентов так, и вот интересно — как у тебя с откликами? Тут реально приходят норм клиенты или в основном молчат?
"""


@bots_error_handler
async def send_messages(clients, user_id, client_id=0):
    sent_count = 0
    targets = await get_all_targets(user_id)
    status = await get_bot_status(clients[client_id].api_id)
    while status == 0:
        client_id += 1
        status = await get_bot_status(clients[client_id].api_id)
    for target in targets:
        if target.f_m:
            continue
        if sent_count >= status:
            client_id += 1
            if client_id == len(clients) - 1:
                break
            status = await get_bot_status(clients[client_id].api_id)
            sent_count = 0
            while status == 0:
                client_id += 1
                status = await get_bot_status(clients[client_id].api_id)
        thread_id = await create_thread()
        init_message = await gpt_assystent_mes(thread_id, mes=f'напиши первое сообщение. пример твоего сообщения: {mes}\n'
                                                              f'используй это только как пример, перепиши его другими словами')
        # init_message = client.beta.threads.messages.create(
        #     thread_id=thread_id,
        #     role="assistant",
        #     content=mes
        # )
        try:
            await clients[client_id].send_message(target.handler, init_message)
        except UsernameNotOccupied as e:
            await update_target(target.handler, {"f_m": True})
            continue
        except UsernameInvalid as e:
            await update_target(target.handler, {"f_m": True})
            continue
        except UsernameNotModified as e:
            await update_target(target.handler, {"f_m": True})
            continue
        await update_target(target.handler, {"f_m": True, 'dialog': thread_id})
        sent_count += 1
        schedule_follow_ups(clients[client_id], target.handler)
        schedule_delete_chat(clients[client_id], target.handler)
        await asyncio.sleep(random.randint(180, 720))
    return client_id
