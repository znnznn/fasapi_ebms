from typing import Type, List, Sequence

from fastapi import Depends, HTTPException
from sqlalchemy import select, Select, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query
from starlette.responses import JSONResponse

from common.constants import ModelType, InputSchemaType
from database import get_async_session
from profiles.models import CompanyProfile, UserProfile
from profiles.schemas import CompanyProfileSchema, UserProfileSchema, UserProfileCreateSchema
from stages.services import BaseService


class CompanyProfileService(BaseService[CompanyProfile, CompanyProfileSchema]):
    def __init__(self, model: Type[CompanyProfile] = CompanyProfile, db_session: AsyncSession = Depends(get_async_session)):
        super(CompanyProfileService, self).__init__(model=model, db_session=db_session)

    async def get(self, id: int = None) -> CompanyProfile:
        stmt = select(self.model)
        company_profile = await self.db_session.scalars(stmt)
        company_profile = company_profile.first()
        if company_profile:
            return company_profile
        stmt = CompanyProfileSchema(working_weekend=False)
        obj = self.create(stmt)
        return await obj


class UserProfileService(BaseService[UserProfile, UserProfileSchema]):
    def __init__(self, model: Type[UserProfile] = UserProfile, db_session: AsyncSession = Depends(get_async_session)):
        super(UserProfileService, self).__init__(model=model, db_session=db_session)

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
        query = self.get_query(limit=limit, offset=offset, user_id=user_id)
        result = await self.db_session.scalars(query)
        return result

    async def create(self, obj: InputSchemaType, user_id: int = None) -> ModelType:
        user_profile_settings = await self.list(user_id=user_id)
        for setting in user_profile_settings:
            if setting.page == obj.page:
                return await self.update(setting.id, obj)
        obj = UserProfileCreateSchema(creator=user_id, **obj.model_dump())
        return await super().create(obj)

    async def delete(self, id: int) -> None | JSONResponse:
        stmt = self.get_query(user_id=id)
        instance = await self.db_session.scalars(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        await self.db_session.delete(instance)
        await self.db_session.commit()
        return JSONResponse(status_code=204, content={"message": f"{self.model.__name__} with id {id} deleted"})
