from aiogram import Router, types, Bot
import asyncio
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter, TelegramUnauthorizedError, TelegramNetworkError
from functools import wraps
from openai import AuthenticationError, RateLimitError, APIConnectionError, APIError
from pyrogram.errors import FloodWait

from instance import logger, bot, client
from aiohttp import ClientConnectorError
from errors.errors import *


router = Router()


@router.error()
async def global_error_handler(update: types.Update, exception: Exception):
    if isinstance(exception, TelegramBadRequest):
        logger.error(f"Некорректный запрос: {exception}. Пользователь: {update.message.from_user.id}")
        return True
    elif isinstance(exception, TelegramRetryAfter):
        logger.error(f"Request limit exceeded. Retry after {exception.retry_after} seconds.")
        await asyncio.sleep(exception.retry_after)
        return True
    elif isinstance(exception, TelegramUnauthorizedError):
        logger.error(f"Authorization error: {exception}")
        return True
    elif isinstance(exception, TelegramNetworkError):
        logger.error(f"Network error: {exception}")
        await asyncio.sleep(5)
        await safe_send_message(bot, update.message.chat.id, text="Повторная попытка...")
        return True
    else:
        logger.exception(f"Неизвестная ошибка: {exception}")
        return True


def db_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Error404 as e:
            logger.exception(str(e))
            return None
        except DatabaseConnectionError as e:
            logger.exception(str(e))
            return None
        except Error409 as e:
            logger.exception(str(e))
            return None
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None
    return wrapper


async def safe_send_message(bott: Bot, recipient, text: str, reply_markup=ReplyKeyboardRemove(), retry_attempts=3, delay=5) -> Message:
    """Отправка сообщения с обработкой ClientConnectorError, поддержкой reply_markup и выбором метода отправки."""

    for attempt in range(retry_attempts):
        try:
            if isinstance(recipient, types.Message):
                msg = await recipient.answer(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            elif isinstance(recipient, types.CallbackQuery):
                msg = await recipient.message.answer(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            elif isinstance(recipient, int):
                msg = await bott.send_message(chat_id=recipient, text=text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                raise TypeError(f"Неподдерживаемый тип recipient: {type(recipient)}")

            return msg

        except ClientConnectorError as e:
            logger.error(f"Ошибка подключения: {e}. Попытка {attempt + 1} из {retry_attempts}.")
            if attempt < retry_attempts - 1:
                await asyncio.sleep(delay)
            else:
                logger.error(f"Не удалось отправить сообщение после {retry_attempts} попыток.")
                return None
        except Exception as e:
            logger.error(str(e))
            return None


def gpt_error_handler(func):
    @wraps(func)
    async def wrapper(*args, retry_attempts=3, delay_between_retries=5, **kwargs):
        for attempt in range(retry_attempts):
            try:
                return await func(*args, **kwargs)
            except AuthenticationError as e:
                logger.exception(f"Authentication Error: {e}")
                return None
            except RateLimitError as e:
                logger.exception(f"Rate Limit Exceeded: {e}")
                return None
            except APIConnectionError as e:
                logger.exception(f"API Connection Error: {e}. Try {attempt + 1}/{retry_attempts}")
                if attempt < retry_attempts - 1:
                    await asyncio.sleep(delay_between_retries)
                else:
                    logger.exception(f"API Connection Error: {e}. All attempts spent {attempt + 1}/{retry_attempts}")
                    return None
            except APIError as e:
                logger.exception(f"API Error: {e}")
                return None
            except Exception as e:
                logger.exception(f"Неизвестная ошибка: {str(e)}")
                return None
    return wrapper


def bots_error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            logger.warning(f"Флуд-лимит: ждем {e.value} секунд...")
            await asyncio.sleep(60)
            client_id = kwargs.get("client_id", 0)
            new_client_id = client_id + 1
            logger.info(f"Повторная попытка с client_id={new_client_id}")
            await safe_send_message(bot, 483458201, text=f"Повтор для {client_id} надо проверить сколько получилось")
            kwargs["client_id"] = new_client_id
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Неизвестная ошибка: {str(e)}")
            return None

    return wrapper


@gpt_error_handler
async def create_thread():
    thread = client.beta.threads.create()
    return thread.id


@gpt_error_handler
async def gpt_assystent_mes(thread_id, assistant_id='asst_DPaR6B9xcB5Phai0yFGwnqK9', mes="давай начнем"):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=mes
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    messages = client.beta.threads.messages.list(thread_id=thread_id)
    data = messages.data[0].content[0].text.value.strip()
    if not data:
        raise ContentError
    else:
        return data
