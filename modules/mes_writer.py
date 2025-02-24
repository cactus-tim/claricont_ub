import asyncio
import random

from database.req import get_all_targets, update_target
from handlers.errors import gpt_assystent_mes, create_thread, bots_error_handler


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
        message_text = await gpt_assystent_mes(thread_id)
        if message_text[-6:-2] == '.docx':
            message_text = message_text[:-17]
        await clients[client_id].send_message(target.handler, message_text)
        await update_target(target.handler, {"f_m": True, 'dialog': thread_id})
        sent_count += 1
        await asyncio.sleep(random.randint(180, 720))
    return client_id
