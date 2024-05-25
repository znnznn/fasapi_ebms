from typing import Type, Sequence

from fastapi import Depends, HTTPException
from sqlalchemy import select, Select, ScalarResult, delete
from sqlalchemy.exc import NoResultFound
from starlette import status
from starlette.responses import JSONResponse, Response

from common.constants import ModelType, InputSchemaType
from database import default_session_maker
from profiles.models import CompanyProfile, UserProfile
from profiles.schemas import CompanyProfileSchema, UserProfileSchema, UserProfileCreateSchema
from stages.services import BaseService


class CompanyProfileService(BaseService[CompanyProfile, CompanyProfileSchema]):
    def __init__(self, model: Type[CompanyProfile] = CompanyProfile):
        super().__init__(model=model)

    async def get(self, id: int = None) -> CompanyProfile:
        async with default_session_maker() as session:
            stmt = select(self.model)
            company_profile = await session.scalars(stmt)
            company_profile = company_profile.first()
            if company_profile:
                return company_profile
            stmt = CompanyProfileSchema(working_weekend=False)
            obj = self.create(stmt)
            return await obj


class UserProfileService(BaseService[UserProfile, UserProfileSchema]):
    def __init__(self, model: Type[UserProfile] = UserProfile):
        super().__init__(model=model)

    def get_query(self, limit: int = None, offset: int = None, user_id: int = None) -> Select:
        query = select(self.model).where(self.model.creator == user_id)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        if limit or offset:
            query = query.order_by(self.model.id)
        return query

    async def list(self, user_id: int = None, limit: int = None, offset: int = None) -> ScalarResult[ModelType]:
        async with default_session_maker() as session:
            query = self.get_query(limit=limit, offset=offset, user_id=user_id)
            result = await session.scalars(query)
            return result

    async def create(self, obj: InputSchemaType, user_id: int = None) -> ModelType:
        user_profile_settings = await self.list(user_id=user_id)
        for setting in user_profile_settings:
            if setting.page == obj.page:
                return await self.update(setting.id, obj)
        obj = UserProfileCreateSchema(creator=user_id, **obj.model_dump())
        return await super().create(obj)

    async def delete(self, id: int) -> None | Response:
        async with default_session_maker() as session:
            stmt = delete(self.model).where(self.model.creator == id)
            await session.execute(stmt)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
