from typing import Optional

from fastapi_users.models import UP
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload


class UserService(SQLAlchemyUserDatabase):
    async def get_by_email(self, email: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        ).options(
            selectinload(self.user_table.category),
            selectinload(self.user_table.user_profiles),
        )
        return await self._get_user(statement)
