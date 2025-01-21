import asyncio

from database.req import get_all_targets, update_target


message_text = ""


async def send_messages(clients, user_id):
    client_id = 0
    sent_count = 0
    targets = await get_all_targets(user_id)
    for target in targets:
        if target.f_m:
            continue
        if sent_count >= 18:
            client_id += 1
            if client_id == len(clients) - 1:
                break
            sent_count = 0
        await clients[client_id].send_message(target.handler, message_text)
        await update_target(target.handler, {"f_m": True})
        sent_count += 1
        await asyncio.sleep(10)
