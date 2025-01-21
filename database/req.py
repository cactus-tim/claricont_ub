from sqlalchemy import select, desc, distinct, and_

from database.models import User, Bot, Target, async_session
from errors.errors import *
from handlers.errors import db_error_handler


@db_error_handler
async def get_all_bots():
    async with async_session() as session:
        bots = await session.execute(select(Bot))
        return bots.scalars().all()


@db_error_handler
async def get_all_targets(user_id: int):
    async with async_session() as session:
        targets = await session.execute(select(Target).where(Target.from_id == user_id))
        return targets.scalars().all()


@db_error_handler
async def add_bot(data: dict):
    async with async_session() as session:
        bot = Bot(**data)
        session.add(bot)
        await session.commit()
        return bot


@db_error_handler
async def get_target(handler: str):
    async with async_session() as session:
        target = await session.scalar(select(Target).where(Target.handler == handler))
        if target:
            return target
        else:
            return None


@db_error_handler
async def add_target(handler: str, from_id: int):
    async with async_session() as session:
        target = await get_target(handler)
        if target:
            raise Error409
        else:
            target = Target(handler=handler, from_id=from_id)
            session.add(target)
            await session.commit()
            return target


@db_error_handler
async def update_target(handler: str, data: dict):
    async with async_session() as session:
        target = await get_target(handler)
        if not target:
            raise Error404
        else:
            for key, value in data.items():
                setattr(target, key, value)
            session.add(target)
            await session.commit()


@db_error_handler
async def get_user(user_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == user_id))
        return user


@db_error_handler
async def create_user(user_id: int):
    async with async_session() as session:
        user = User(id=user_id)
        session.add(user)
        await session.commit()
        return user


@db_error_handler
async def update_user(user_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(user_id)
        if not user:
            raise Error404
        else:
            for key, value in data.items():
                setattr(user, key, value)
            session.add(user)
            await session.commit()
            return user


@db_error_handler
async def get_all_users():
    async with async_session() as session:
        users = await session.execute(select(User))
        return users.scalars().all()
