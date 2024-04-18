from collections import defaultdict
from typing import Generic, Type, Optional, List

from fastapi import Depends, HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select, ScalarResult, func, and_, case, Result, Sequence, union_all, literal
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query

from common.constants import InputSchemaType, OriginModelType
from common.filters import RenameFieldFilter
from database import get_async_session
from origin_db.filters import CategoryFilter
from origin_db.models import Inprodtype, Arinvdet, Arinv, Inventry
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema, InventrySchema
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


class BaseService(Generic[OriginModelType, InputSchemaType]):
    default_ordering_field = 'recno5'

    def __init__(
            self, model: Type[OriginModelType], db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[RenameFieldFilter] = None
    ):
        self.model = model
        self.db_session = db_session
        self.filter = list_filter

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
        query = select(self.model).where(and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR))
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def get_object_or_404(self, autoid: str) -> OriginModelType:
        obj = await self.get(autoid)
        return obj

    async def count_query_objs(self, query) -> int:
        return await self.db_session.scalar(select(func.count()).select_from(query.subquery()))

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        count = await self.count_query_objs(self.get_query())
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query(limit=limit, offset=offset, **kwargs))
        return {
            "count": count,
            "results": objs.all(),
        }

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        stmt = self.get_query().where(self.model.autoid == autoid)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def list(self, kwargs: Optional[dict] = None) -> Sequence[OriginModelType]:
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query())
        return objs.all()

    async def get_listy_by_autoids(self, autoids: List[str]) -> Sequence[OriginModelType]:
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query().where(self.model.autoid.in_(autoids)))
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

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]):
        query = select(self.model).where(
            and_(
                self.model.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
            )
        ).order_by(self.model.prod_type)
        if self.filter:
            query = self.filter.filter(query, **kwargs)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def get_category_autoid_by_name(self, name: str) -> Inprodtype:
        smtp = self.get_query().where(self.model.prod_type == name)
        result = await self.db_session.scalars(smtp)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {name} not found")


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(
            self, model: Type[Arinvdet] = Arinvdet,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]):
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
        ).group_by(
            self.model
        )
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        else:
            query = query.order_by(getattr(self.model, self.default_ordering_field))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        return await self.paginated_list(limit=limit, offset=offset, **kwargs)

    async def list_by_orders(self, autoids: List[str]):
        stmt = self.get_query().where(self.model.doc_aid.in_(autoids))
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_origin_item_with_item(self, autoid: str):
        return await self.get(autoid)


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(
            self, model: Type[Arinv] = Arinv,
            db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    # async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
    #     count = await self.count_query_objs(super().get_query())
    #     objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query(limit=limit, offset=offset, **kwargs))
    #     return {"count": count, "results": objs.all()}

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]):
        # det = select(
        #     Arinvdet, Inventry.prod_type
        # ).join(
        #     Arinvdet.rel_inventry
        # ).join(
        #     Arinvdet.order
        # ).where(
        #     and_(
        #         Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
        #         Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
        #         Inventry.prod_type.isnot(None),
        #         Arinvdet.par_time == '',
        #         Arinvdet.inven != None,
        #         Arinvdet.inven != '',
        #     ),
        # ).options(
        #     selectinload(Arinvdet.rel_inventry),
        #     selectinload(Arinvdet.order),
        # ).group_by(
        #     Arinvdet
        # ).subquery()
        # sbq = aliased(Arinvdet, det, name="details")
        # ).scalar_subquery().correlate(Inventry)
        query = select(
            self.model,
        ).where(
            and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR)
        ).join(
            # sbq, sbq.doc_aid == self.model.autoid
            self.model.details,
        ).join(
            Inventry
        ).where(
            and_(
                Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
                # Arinvdet.autoid.in_(det),
                Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                Inventry.prod_type.isnot(None),
                Arinvdet.par_time == '',
            ),
        ).options(
            # contains_eager(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
            selectinload(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
        ).group_by(
            self.model
        )
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        else:
            query = query.order_by(getattr(self.model, self.default_ordering_field))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        return await self.paginated_list(limit=limit, offset=offset, **kwargs)

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

    async def get_origin_order_with_sales_order(self, autoid: str) -> Optional[OriginModelType]:
        return await self.get(autoid)


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

    async def count_capacity_by_days(self, items_data: dict) -> Sequence[Result]:
        """  Return total capacity for an inventory group by prod type with count arinv"""
        compair_data = defaultdict(list)
        for autoid, date in items_data.items():
            compair_data[date.strftime('%Y-%m-%d')].append(autoid)
        list_subqueries = []
        for production_date, autoids in compair_data.items():
            stmt = select(
                self.model.prod_type,
                literal(production_date).label("production_date"),
                func.count(Arinvdet.doc_aid).label("count_orders"),
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
                self.model.prod_type,
            )

            list_subqueries.append(stmt)
        list_subqueries = union_all(*list_subqueries)
        list_subqueries_alias = list_subqueries.alias('list_subqueries_alias')
        stmt = select(
            list_subqueries_alias.c.production_date, list_subqueries_alias.c.total_capacity, list_subqueries_alias.c.prod_type,
            list_subqueries_alias.c.count_orders,
        )
        objs = await self.db_session.execute(stmt)
        result = objs.all()
        return result
