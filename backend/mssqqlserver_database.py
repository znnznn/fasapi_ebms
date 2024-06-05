from typing import List

import aioodbc
from aioodbc.cursor import Cursor
from fastapi import HTTPException
from pyodbc import OperationalError
from concurrent.futures import ThreadPoolExecutor
import asyncio
from starlette import status
from fastapi import APIRouter, Depends, Query

from settings import EBMS_DB

loop = asyncio.get_event_loop()


async def get_cursor() -> Cursor:
    driver = '{ODBC Driver 17 for SQL Server}'
    dsn = f'Driver={driver};Server={EBMS_DB.DB_HOST},{EBMS_DB.DB_PORT};Database={EBMS_DB.DB_NAME};UID={EBMS_DB.DB_USER};PWD={EBMS_DB.DB_PASS};Trusted_Connection=no;'
    try:
        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="DB connectivity failed")

