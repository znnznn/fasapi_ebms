from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from common.models import EBMSBase, DefaultBase
from settings import EBMS_DB, Default_DB
from users.models import User
from users.services import UserService

engines = {
    EBMSBase: create_async_engine('mssql+aioodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'.format(
        EBMS_DB.DB_USER, EBMS_DB.DB_PASS, EBMS_DB.DB_HOST, EBMS_DB.DB_PORT, EBMS_DB.DB_NAME),
        pool_size=30, max_overflow=40
    ),
    DefaultBase: create_async_engine('postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
        Default_DB.DB_USER, Default_DB.DB_PASS, Default_DB.DB_HOST, Default_DB.DB_PORT, Default_DB.DB_NAME),
        pool_size=30, max_overflow=40
    ),
}

async_session_maker = async_sessionmaker(binds=engines, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield UserService(session, User)
