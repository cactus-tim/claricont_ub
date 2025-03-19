import asyncio
import random
import datetime

from pyrogram.errors import UsernameNotOccupied, UsernameInvalid, UsernameNotModified

from database.req import get_all_targets, update_target
from handlers.errors import gpt_assystent_mes, create_thread, bots_error_handler
from instance import client, scheduler


mes = """
Привет! Видел ты ищешь заказы в чатах в телеграме.\n
Я недавно тоже начал искать клиентов так, и вот интересно — как у тебя с откликами? Тут реально приходят норм клиенты или в основном молчат?
"""


messages = [
    'Подниму сообщение, если вдруг оно укатилось. Тема реально интересная, сам недавно с этим разбирался.',
    'Понимаю, что можете быть заняты, но всё же интересно, что думаете.',
    'Ладно, больше не буду отвлекать. Если вдруг интересно, могу просто скинуть то, что сам недавно нашёл – штука, которая помогает с поиском. Без спама, просто вдруг пригодится. 😉'
]


async def follow_up_message(send_client, target_handler: str, message: str):
    try:
        await send_client.send_message(target_handler, message)
    except Exception as e:
        print(f"Ошибка при отправке follow-up сообщения {target_handler}: {e}")


def schedule_follow_ups(send_client, target_handler: str):
    delays = [6, 24, 48]
    for hours, m in delays, messages:
        run_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
        scheduler.add_job(follow_up_message, 'date', run_date=run_time, args=[send_client, target_handler, m])


@bots_error_handler
async def send_messages(clients, user_id, client_id=0):
    sent_count = 0
    targets = await get_all_targets(user_id)
    for target in targets:
        if target.f_m:
            continue
        if sent_count >= 10:
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
        except UsernameInvalid as e:
            await update_target(target.handler, {"f_m": True})
            continue
        except UsernameNotModified as e:
            await update_target(target.handler, {"f_m": True})
            continue
        await update_target(target.handler, {"f_m": True, 'dialog': thread_id})
        sent_count += 1
        schedule_follow_ups(clients[client_id], target.handler)
        await asyncio.sleep(random.randint(180, 720))
    return client_id
