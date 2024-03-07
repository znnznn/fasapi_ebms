from typing import Generic, Type, Optional, List

from fastapi import Depends, HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select, ScalarResult, func, and_, or_, case, Result, Sequence
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, subqueryload, with_loader_criteria

from common.constants import InputSchemaType, OriginModelType
from database import get_async_session
from origin_db.filters import CategoryFilter
from origin_db.models import Inprodtype, Arinvdet, Arinv, Inventry
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema, InventrySchema
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


class BaseService(Generic[OriginModelType, InputSchemaType]):
    default_ordering_field = 'recno5'

    def __init__(
            self, model: Type[OriginModelType], db_session: AsyncSession = Depends(get_async_session), list_filter: Optional[Filter] = None
    ):
        self.model = model
        self.db_session = db_session
        self.filter = list_filter

    def get_query(self, limit: int = None, offset: int = None):
        query = select(self.model).where(and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR))
        if self.filter:
            print(2)
            query = self.filter.filter(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def count_query_objs(self, query) -> int:
        return await self.db_session.scalar(select(func.count()).select_from(query.subquery()))

    async def paginated_list(self, limit: int = 10, offset: int = 0) -> dict:
        count = await self.count_query_objs(self.get_query())
        objs: ScalarResult[Inprodtype] = await self.db_session.scalars(self.get_query(limit=limit, offset=offset))
        return {
            "count": count,
            "results": objs.all(),
        }

    async def get(self, autoid: int) -> Optional[OriginModelType]:
        stmt = select(self.model).where(self.model.autoid == autoid)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def list(self):
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query())
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
    def __init__(
            self, model: Type[Inprodtype] = Inprodtype,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[CategoryFilter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None):
        query = select(self.model).where(
            and_(
                self.model.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
            )
        ).order_by(self.model.prod_type)
        if self.filter:
            query = self.filter.filter(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(
            self, model: Type[Arinvdet] = Arinvdet,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None):
        query = select(
            self.model
        ).join(
            self.model.rel_inventry
        ).join(
            self.model.order
        ).where(
            and_(
                self.model.inv_date >= FILTERING_DATA_STARTING_YEAR,
                Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                self.model.par_time == '',
                self.model.inven != None,
                self.model.inven != '',
            ),
        ).options(
            selectinload(self.model.rel_inventry),
            selectinload(self.model.order),
        ).order_by(
            getattr(self.model, self.default_ordering_field)
        ).group_by(
            self.model
        )
        if self.filter:
            query = self.filter.filter(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def list(self, limit: int = 10, offset: int = 0) -> dict:
        return await self.paginated_list(limit=limit, offset=offset)


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(
            self, model: Type[Arinv] = Arinv,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None):
        query = select(
            self.model,
        ).where(
            and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR)
        ).join(
            Arinvdet
        ).options(
            selectinload(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
        ).order_by(
            getattr(self.model, self.default_ordering_field)
        ).group_by(
            self.model
        )
        if self.filter:
            query = self.filter.filter(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def list(self, limit: int = 10, offset: int = 0) -> dict:
        return await self.paginated_list(limit=limit, offset=offset)

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
            getattr(self.model, self.default_ordering_field)
        ).group_by(
            self.model
        )
        result = await self.db_session.scalars(query)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")


class InventryService(BaseService[Inventry, InventrySchema]):
    def __init__(
            self, model: Type[Inventry] = Inventry,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    async def count_capacity(self, autoids: list[str]) -> Result:
        """  Return total capacity for an inventory group by prod type """
        stmt = select(
            self.model.prod_type,
            func.sum(case(
                (self.model.prod_type == 'Trim', Arinvdet.demd),
                (Arinvdet.heightd != 0, ((Arinvdet.heightd / 12) * Arinvdet.quan)),
                else_=Arinvdet.quan
            )).label("total_capacity"),
        ).where(
            Arinvdet.autoid.in_(autoids), Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES), Arinvdet.par_time == '',
        ).join(
            self.model.arinvdet,
        ).group_by(
            self.model.prod_type
        )
        return await self.db_session.execute(stmt)
