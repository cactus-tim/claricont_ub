import asyncio
from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from confige import BotConfig
from database.req import *
from handlers import errors, user
from instance import bot, init_accounts, scheduler
from database.models import async_main
from modules.mes_writer import send_messages
from modules.mes_handler import setup_handlers


def register_routers(dp: Dispatcher) -> None:
    dp.include_routers(errors.router, user.router)


async def schedule_tasks(clients, users):
    async def daily_task():
        for user in users:
            await send_messages(clients, user_id=user.id)

    scheduler.add_job(daily_task, 'interval', days=1)
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

    users = await get_all_users()
    await schedule_tasks(clients, users)

    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as _ex:
        print(f'Exception: {_ex}')
    finally:
        await shutdown(clients)


if __name__ == '__main__':
    asyncio.run(main())