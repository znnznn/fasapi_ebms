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
    dsn = rf'Driver=Driver=ODBC Driver 17 for SQL Server;Server={EBMS_DB.DB_HOST},{EBMS_DB.DB_PORT};Database={EBMS_DB.DB_NAME};UID={EBMS_DB.DB_USER};PWD={EBMS_DB.DB_PASS};Trusted_Connection=no;'
    try:
        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="DB connectivity failed")


def get_quoted(value):
    return f"'{value}'"


async def get_fallout_details_db(db: Cursor, country: List,
                                 start_interface_load_date: str,
                                 end_interface_load_date: str,
                                 record_status=False):
    if record_status:
        query = fr"select * FROM [PRISM].[PR_fallout_output] where Country in ({(', '.join(map(lambda x: get_quoted(x), country)))}) and Interface__Load_Date >= '{start_interface_load_date}' and Interface__Load_Date <= '{end_interface_load_date}' and Record_Status = 'Open';"
    else:
        query = fr"select * FROM [PRISM].[PR_fallout_output] where Country in ({(', '.join(map(lambda x: get_quoted(x), country)))}) and Interface__Load_Date >= '{start_interface_load_date}' and Interface__Load_Date <= '{end_interface_load_date}';"
    await db.execute(query)
    records = await db.fetchall()
    column_names = [column[0] for column in db.description]
    out = []
    for record in records:
        out.append(dict(zip(column_names, record)))
    return out


@router.get('/get_fallout_details', status_code=status.HTTP_200_OK)
async def get_fallout_details(start_interface_load_date: str,
                              end_interface_load_date: str,
                              record_status=False, db: Cursor = Depends(get_cursor),
                              country: List[str] = Query(...)):
    return await get_fallout_details_db(country=country, start_interface_load_date=start_interface_load_date,
                                        end_interface_load_date=end_interface_load_date, record_status=record_status,
                                        db=db)
