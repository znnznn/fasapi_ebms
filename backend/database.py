from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Depends
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.models import EBMSBase, DefaultBase
from settings import EBMS_DB, Default_DB, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB
from users.models import User
from users.services import UserService

engines = {
    EBMSBase: create_async_engine('mssql+aioodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'.format(
        EBMS_DB.DB_USER, EBMS_DB.DB_PASS, EBMS_DB.DB_HOST, EBMS_DB.DB_PORT, EBMS_DB.DB_NAME),
        pool_size=70, max_overflow=30, pool_pre_ping=True, isolation_level="SERIALIZABLE", pool_recycle=3600,
        connect_args={"server_settings": {"jit": "off"}}, execution_options={
        "isolation_level": "REPEATABLE READ"
    }
    ),
    DefaultBase: create_async_engine('postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
        Default_DB.DB_USER, Default_DB.DB_PASS, Default_DB.DB_HOST, Default_DB.DB_PORT, Default_DB.DB_NAME),
        max_overflow=30, pool_recycle=3600,
        connect_args={"server_settings": {"jit": "off"}},
    ),
}

async_session_maker = async_sessionmaker(binds=engines, expire_on_commit=False)
ebms_engine = create_async_engine('mssql+aioodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'.format(
        EBMS_DB.DB_USER, EBMS_DB.DB_PASS, EBMS_DB.DB_HOST, EBMS_DB.DB_PORT, EBMS_DB.DB_NAME),
        pool_size=70, max_overflow=30, pool_pre_ping=True, isolation_level="SERIALIZABLE", pool_recycle=3600,
    )

default_engine = create_async_engine('postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
        Default_DB.DB_USER, Default_DB.DB_PASS, Default_DB.DB_HOST, Default_DB.DB_PORT, Default_DB.DB_NAME),
        pool_size=70, max_overflow=30, pool_pre_ping=True, pool_recycle=600
    )

ebms_engine.connect()

ebms_session_maker = async_sessionmaker(bind=ebms_engine, expire_on_commit=False, autoflush=False, autocommit=False)

default_session_maker = async_sessionmaker(bind=default_engine, expire_on_commit=False, autoflush=False, autocommit=False)


@lru_cache(maxsize=None)
def get_ebms_engine():
    return ebms_engine


@lru_cache(maxsize=None)
def get_default_engine():
    return default_engine


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_ebms_session() -> AsyncGenerator[AsyncSession, None]:
    async with ebms_session_maker() as session:
        yield session


async def get_default_session() -> AsyncGenerator[AsyncSession, None]:
    async with default_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_default_session)):
    yield UserService(session, User)


def create_redis_pool():
    return aioredis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, db=REDIS_DB)


redis_pool = create_redis_pool()
