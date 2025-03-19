from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ARRAY, BigInteger, ForeignKey, Numeric, JSON, Date
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from instance import async_session, engine


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user2"

    id = Column(BigInteger, primary_key=True, nullable=False, index=True)
    is_superuser = Column(Boolean, default=False)


class Bot(Base):
    __tablename__ = "bot"

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    name = Column(String, nullable=False)
    api_id = Column(BigInteger, nullable=False)
    api_hash = Column(String, nullable=False)
    # TODO: Add more fields


class Target(Base):
    __tablename__ = "target"

    id = Column(Integer, primary_key=True, index=True, nullable=False, autoincrement=True)
    from_id = Column(BigInteger, foreign_key="user2.tg_id", nullable=False)
    handler = Column(String, nullable=False)
    f_m = Column(Boolean, default=False)
    f_a = Column(Boolean, default=False)
    l_m = Column(Boolean, default=False)
    dialog = Column(String, default='')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
