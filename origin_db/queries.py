from select import select

from sqlalchemy import insert

from database import User


async def get_list_of_orders(session):
    stmt = select(User).where(User.username == "admin")
    await session.execute(stmt)
    await session.commit()
    return {"message": "inserted"}
