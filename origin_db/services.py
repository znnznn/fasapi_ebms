from typing import Generic, Type, Optional

from fastapi import Depends, HTTPException
from sqlalchemy import select, ScalarResult, func, and_, or_
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, subqueryload, with_loader_criteria

from common.constants import InputSchemaType, OriginModelType
from database import get_async_session
from origin_db.models import Inprodtype, Arinvdet, Arinv, Inventry
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


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
        stmt = select(self.model).where(and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR))
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

    async def list(self):
        stmt = select(self.model).where(
            and_(
                self.model.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
            )
        )
        objs: ScalarResult[Inprodtype] = await self.db_session.scalars(stmt)
        return objs.all()


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(self, model: Type[Arinvdet] = Arinvdet, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def list(self, limit: int = 10, offset: int = 0) -> dict:
        query = select(
            self.model,
        ).join(
            self.model.rel_inventry
        ).join(
            self.model.order
        ).where(
            and_(
                # self.model.inv_date >= FILTERING_DATA_STARTING_YEAR,
                # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                # self.model.par_time == '',
                # self.model.inven != None,
                # self.model.inven != '',
            ),
        ).options(
            selectinload(self.model.rel_inventry),
            selectinload(self.model.order),
        ).order_by(
            self.model.recno5
        ).group_by(
            self.model
        )
        count = await self.db_session.scalar(select(func.count()).select_from(query.subquery()))
        objs = await self.db_session.scalars(query.limit(limit).offset(offset))
        return {
            "count": count,
            "results": objs.all(),
        }


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(self, model: Type[Arinv] = Arinv, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def list(self, limit: int = 10, offset: int = 0) -> dict:
        query = select(
            self.model,
        ).where(
            and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR)
        ).join(
            Arinvdet
        ).options(
            selectinload(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
        ).order_by(
            Arinv.recno5
        ).group_by(
            self.model
        )
        count = await self.db_session.scalar(select(func.count()).select_from(query.subquery()))
        objs = await self.db_session.scalars(query.limit(limit).offset(offset))
        return {
            "count": count,
            "results": objs.all(),
        }

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        query = select(
            self.model,
        ).where(
            self.model.autoid == autoid
        ).join(
            Arinvdet
        ).options(
            selectinload(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
        ).order_by(
            Arinv.recno5
        ).group_by(
            self.model
        )
        result = await self.db_session.scalars(query)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")
