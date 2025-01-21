from aiogram import Bot
from aiogram.enums import ParseMode
import os
from dotenv import load_dotenv
import sys
from aiogram.client.bot import DefaultBotProperties
import logging
import asyncio
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler


from database.req import get_all_bots


sys.path.append(os.path.join(sys.path[0], 'k_bot'))

load_dotenv('.env')
token = os.getenv('TOKEN_API_TG')
SQL_URL_RC = (f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}'
              f'@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


scheduler = AsyncIOScheduler()


async def init_accounts():
    accounts = []
    _accounts = await get_all_bots()
    for account in _accounts:
        client = Client(
            account.session_name,
            api_id=account.api_id,
            api_hash=account.api_hash,
        )
        accounts.append(client)
    return accounts


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


logger = logging.getLogger(__name__)
