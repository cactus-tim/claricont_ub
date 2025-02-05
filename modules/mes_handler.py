from pyrogram import filters


from database.req import get_target
from handlers.errors import gpt_assystent_mes


def setup_handlers(client):
    @client.on_message(filters.private)
    async def reply(client, message):
        target = await get_target("@" + message.from_user.username)
        if not target:
            return
        if not target.f_m:
            return
        message_text = await gpt_assystent_mes(target.dialog, mes=message.text)
        await client.send_message(target.handler, message_text)
