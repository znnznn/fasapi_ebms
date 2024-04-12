from typing import Optional

from fastapi_users.models import UP
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy import select, func, Select, ScalarResult
from sqlalchemy.orm import selectinload

from common.constants import ModelType


class UserService(SQLAlchemyUserDatabase):
    def get_query(self, limit: int = None, offset: int = None, **kwargs) -> Select:
        query = select(self.user_table).options(
            selectinload(self.user_table.category),
            selectinload(self.user_table.user_profiles),
        )
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        if limit or offset:
            query = query.order_by(self.user_table.id)
        return query

    async def count_query_objs(self, query) -> int:
        return await self.session.scalar(select(func.count()).select_from(query.subquery()))

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        count = await self.count_query_objs(self.get_query())
        objs: ScalarResult[ModelType] = await self.session.scalars(self.get_query(limit=limit, offset=offset, **kwargs))
        return {
            "count": count,
            "results": objs.all(),
        }

    async def get_by_email(self, email: str) -> Optional[UP]:
        statement = select(self.user_table).where(
            func.lower(self.user_table.email) == func.lower(email)
        ).options(
            selectinload(self.user_table.category),
            selectinload(self.user_table.user_profiles),
        )
        return await self._get_user(statement)

    async def list(self, limit: int = 10, offset: int = 0, **kwargs) -> Optional[UP]:
        results = await self.session.scalars(self.get_query(limit=limit, offset=offset))
        return results.all()
