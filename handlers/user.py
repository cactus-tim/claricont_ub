from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.errors import safe_send_message
from instance import bot
from database.req import *

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await get_user(message.from_user.id)
    if not user:
        await create_user(message.from_user.id)
    await safe_send_message(bot, message, text="")


@router.message(Command("info"))
async def cmd_info(message: Message):
    await safe_send_message(bot, message, text="")


@router.message(Command("add_targets"))
async def cmd_add_targets(message: Message):
    pass
