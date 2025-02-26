import asyncio
import random

from pyrogram.errors import UsernameNotOccupied

from database.req import get_all_targets, update_target
from handlers.errors import gpt_assystent_mes, create_thread, bots_error_handler
from instance import client


mes = """
Привет! Видел ты ищешь заказы в чатах в телеграме.\n
Я недавно тоже начал искать клиентов так, и вот интересно — как у тебя с откликами? Тут реально приходят норм клиенты или в основном молчат?
"""


@bots_error_handler
async def send_messages(clients, user_id, client_id=0):
    sent_count = 0
    targets = await get_all_targets(user_id)
    for target in targets:
        if target.f_m:
            continue
        if sent_count >= 6:
            client_id += 1
            if client_id == len(clients) - 1:
                break
            sent_count = 0
        thread_id = await create_thread()
        init_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="assistant",
            content=mes
        )
        try:
            await clients[client_id].send_message(target.handler, mes)
        except UsernameNotOccupied as e:
            await update_target(target.handler, {"f_m": True})
            continue
        await update_target(target.handler, {"f_m": True, 'dialog': thread_id})
        sent_count += 1
        await asyncio.sleep(random.randint(180, 720))
    return client_id
