from datetime import datetime
from typing import AsyncGenerator, Optional, Any, Union

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, String, Boolean, func, TIMESTAMP, inspect, create_engine, ClauseElement, Engine, Connection
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy.orm._typing import _O
from sqlalchemy.orm.session import _EntityBindKey, _SessionBind
from sqlalchemy_utils import EmailType, ChoiceType

from common.constants import Role
from common.models import EBMSBase, DefaultBase
from settings import EBMS_DB, Default_DB
from users.models import User


# EBMS_DATABASE_URL = 'mssql+aioodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'.format(
#     DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME
# )

engines = {
    EBMSBase: create_async_engine('mssql+aioodbc://{}:{}@{}:{}/{}?driver=ODBC+Driver+17+for+SQL+Server'.format(
        EBMS_DB.DB_USER, EBMS_DB.DB_PASS, EBMS_DB.DB_HOST, EBMS_DB.DB_PORT, EBMS_DB.DB_NAME)),
    DefaultBase: create_async_engine('postgresql+asyncpg://{}:{}@{}:{}/{}'.format(
        Default_DB.DB_USER, Default_DB.DB_PASS, Default_DB.DB_HOST, Default_DB.DB_PORT, Default_DB.DB_NAME)),
}

async_session_maker = async_sessionmaker(binds=engines, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
