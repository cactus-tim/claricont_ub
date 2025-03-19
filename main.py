import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.errors import UserDeactivatedBan
from pyrogram.session import Session

from confige import BotConfig
from database.req import *
from handlers import errors, user
from instance import bot, scheduler, Client, logger
from database.models import async_main
from modules.mes_writer import send_messages
from modules.mes_handler import setup_handlers


async def init_accounts():
    accounts = []
    _accounts = await get_all_bots()
    for account in _accounts:
        # client = Client(account.hash,
        #                 session=Session(client=account.hash, dc_id=account.dc_id, auth_key=account.auth_key,
        #                                 test_mode=account.test_mode))
        client = Client(account.name, api_id=account.api_id, api_hash=account.api_id)
        accounts.append(client)
    return accounts


def register_routers(dp: Dispatcher) -> None:
    dp.include_routers(errors.router, user.router)


async def schedule_tasks(clients, users):
    async def daily_task():
        client_id = 0
        for user in users:
            client_id = await send_messages(clients, user.id, client_id=client_id)

    scheduler.add_job(daily_task, 'interval', days=1, start_date='2023-10-01 12:00:00', timezone='Europe/Moscow')
    await daily_task()


async def shutdown(clients):
    for client in clients:
        await client.stop()
    scheduler.shutdown()


async def main() -> None:
    await async_main()

    config = BotConfig(
        admin_ids=[],
        welcome_message=""
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp["config"] = config

    register_routers(dp)

    scheduler.start()

    clients = await init_accounts()
    good_clients = []
    for client in clients:
        setup_handlers(client)
        try:
            await client.start()
            await client.send_message('@If9090', "Ready")
            good_clients.append(client)
        except UserDeactivatedBan as e:
            logger.warning(f"Клиент с api_id {client.api_id} заблокирован: {e}")
            await bot.send_message(483458201, text=f"Клиент с api_id {client.api_id} заблокирован")
            await delete_bot(client.api_id)
            await bot.send_message(483458201, text=f"Клиент с api_id {client.api_id} удален")
            continue

    users = await get_all_users()
    # await schedule_tasks(good_clients, users)

    try:
        # await send_messages(clients, 483458201)
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')
    finally:
        await bot.send_message(483458201, text="We are down")
        await shutdown(good_clients)


if __name__ == '__main__':
    asyncio.run(main())
