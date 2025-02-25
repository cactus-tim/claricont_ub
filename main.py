import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.session import Session

from confige import BotConfig
from database.req import *
from handlers import errors, user
from instance import bot, scheduler, Client
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
            client_id = await send_messages(clients, user.id, client_id)

    scheduler.add_job(daily_task, 'interval', days=1, start_date='2023-10-01 12:00:00', timezone='Europe/Moscow')
    await daily_task()
    scheduler.start()


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

    clients = await init_accounts()
    for client in clients:
        setup_handlers(client)
        await client.start()
        await client.send_message('@If9090', "Ready")

    users = await get_all_users()
    await schedule_tasks(clients, users)

    try:
        # await send_messages(clients, 52786051)
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')
    finally:
        await shutdown(clients)


if __name__ == '__main__':
    asyncio.run(main())
