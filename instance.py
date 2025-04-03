from aiogram import Bot
from aiogram.enums import ParseMode
import os

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from dotenv import load_dotenv
import sys
from aiogram.client.bot import DefaultBotProperties
from openai import OpenAI
import logging
import asyncio
from pyrogram import Client
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


sys.path.append(os.path.join(sys.path[0], 'k_bot'))

load_dotenv('.env')
token = os.getenv('TOKEN_API_TG')
SQL_URL_RC = (f'postgresql+asyncpg://{os.getenv("DB_USER")}:{os.getenv("DB_PASS")}'
              f'@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}')

jobstores = {
    'default': SQLAlchemyJobStore(url=SQL_URL_RC)
}


engine = create_async_engine(url=SQL_URL_RC, echo=True)
async_session = async_sessionmaker(engine)


bot = Bot(
    token=token,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML
    )
)


scheduler = AsyncIOScheduler()


logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


logger = logging.getLogger(__name__)


token = os.getenv('TOKEN_API_GPT')
client = OpenAI(api_key=token)


links = ['@fathers_of_traffic', '@clickhouse_ru', '@biznesprodaji', '@pf_avito_chat1', '@investory_maison', '@avito_prosto']
messages = [
    "Привет! Чем могу помочь?",
    "Добро пожаловать! Чем заинтересован сегодня?",
    "Спасибо за обращение. Жду вашего запроса.",
    "Рад помочь вам!",
    "Какой вопрос у вас возник?",
    "Пожалуйста, опишите вашу проблему.",
    "Обработка запроса, пожалуйста, подождите.",
    "Ваш запрос принят.",
    "Спасибо за ваше сообщение.",
    "Чем еще могу помочь?",
    "Если у вас возникли дополнительные вопросы, пишите.",
    "Пожалуйста, уточните ваш вопрос.",
    "Запрос отправлен администратору.",
    "Ваш запрос успешно обработан.",
    "Пожалуйста, проверьте ваши данные.",
    "Сообщение принято. Ожидайте ответа.",
    "Спасибо, что обратились к нам!",
    "Ваш запрос в процессе выполнения.",
    "Успешное завершение операции.",
    "Операция не удалась. Попробуйте позже.",
    "Ошибка! Пожалуйста, попробуйте снова.",
    "Система временно недоступна.",
    "Пожалуйста, перезагрузите приложение.",
    "Спасибо за ваше терпение.",
    "Запрос обрабатывается. Подождите, пожалуйста.",
    "Ожидайте, ваш запрос в очереди.",
    "Пожалуйста, введите корректные данные.",
    "Мы ценим ваш интерес!",
    "Ваше сообщение отправлено.",
    "Подключение установлено.",
    "Соединение прервано. Попробуйте позже.",
    "Вы успешно зарегистрированы.",
    "Новый пользователь успешно добавлен.",
    "Учетная запись обновлена.",
    "Вход выполнен успешно.",
    "Неверные данные для входа.",
    "Пожалуйста, войдите в систему.",
    "Вы уже вошли в систему.",
    "Выход выполнен успешно.",
    "Спасибо за использование нашего сервиса.",
    "Ваш отзыв важен для нас.",
    "Оставьте ваш комментарий.",
    "Сообщите нам о найденной ошибке.",
    "Пожалуйста, ознакомьтесь с правилами.",
    "Действие отменено пользователем.",
    "Запрос не найден.",
    "Информация обновлена.",
    "Начинается процесс загрузки данных.",
    "Загрузка завершена успешно.",
    "До новых встреч!"
]
