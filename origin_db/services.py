from typing import Generic, Type, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select, ScalarResult
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from common.constants import InputSchemaType, OriginModelType
from database import get_async_session
from origin_db.models import Inprodtype, Arinvdet, Arinv
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema


class BaseService(Generic[OriginModelType, InputSchemaType]):
    def __init__(self, model: Type[OriginModelType], db_session: AsyncSession = Depends(get_async_session)):
        self.model = model
        self.db_session = db_session

    async def get(self, autoid: int) -> Optional[OriginModelType]:
        stmt = select(self.model).where(self.model.autoid == autoid)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def list(self):
        stmt = select(self.model)
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(stmt)
        return objs.all()

    async def create(self, obj: InputSchemaType) -> OriginModelType:
        """ Not allowed to create """
        raise NotImplementedError

    async def update(self, autoid: int, obj: InputSchemaType) -> Optional[OriginModelType]:
        """ Not allowed to update """
        raise NotImplementedError

    async def partial_update(self, autoid: int, obj: InputSchemaType) -> Optional[OriginModelType]:
        """ Not allowed to update """
        raise NotImplementedError

    async def delete(self, autoid: int) -> Optional[OriginModelType]:
        """ Not allowed to delete """
        raise NotImplementedError


class CategoryService(BaseService[Inprodtype, CategorySchema]):
    def __init__(self, model: Type[Inprodtype] = Inprodtype, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    # async def list(self):
    #     query = select(Inprodtype).group_by(Inprodtype)
    #     objs = await self.db_session.scalars(query)
    #     return objs.all()


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(self, model: Type[Arinvdet] = Arinvdet, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(self, model: Type[Arinv] = Arinv, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def list(self):
        query = select(self.model).options(selectinload(self.model.details, Arinvdet.rel_item)).group_by(Arinv)
        objs: ScalarResult[Arinv] = await self.db_session.scalars(query)
        return objs.all()
