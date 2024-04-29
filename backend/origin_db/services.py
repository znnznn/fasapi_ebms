import time
from collections import defaultdict
from typing import Generic, Type, Optional, List, NamedTuple

import sqlalchemy
from fastapi import Depends, HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select, ScalarResult, func, and_, case, Result, Sequence, union_all, literal, text, literal_column
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query, contains_eager

from common.constants import InputSchemaType, OriginModelType
from common.filters import RenameFieldFilter
from database import get_async_session, get_ebms_session, ebms_connection, ebms_engine
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
        start_time = time.time()
        print("count count")
        # sql_text = str(select(func.count()).select_from(query.subquery()).compile(compile_kwargs={"literal_binds": True}, dialect='mssql'))
        # print(sql_text)
        # result = await self.db_session.execute(text(sql_text))
        # print(result)
        print(time.time() - start_time)
        return await self.db_session.scalar(select(func.count()).select_from(query.subquery()))

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict],) -> dict:
        list_query = self.get_query(limit=limit, offset=offset, **kwargs)
        count_sql = str(select(
            func.count()).select_from(self.get_query().subquery()
        ).compile(compile_kwargs={"literal_binds": True}, dialect=sqlalchemy.dialects.mssql.dialect()))
        sql_text = str(list_query.compile(compile_kwargs={"literal_binds": True}, dialect=sqlalchemy.dialects.mssql.dialect()))
        # print(sql_text)
        async with AsyncSession(ebms_engine) as session:
            count = await session.execute(text(count_sql))
            data = await session.execute(text(sql_text))
        time_start = time.time()
        data_all = data.all()
        print(data_all)
        list_objs = [data._asdict() for data in data_all]

        list_objs_as_model = []
        for obj in list_objs:
            data_to_lower_key = {}
            for k, v in obj.items():
                data_to_lower_key[k.lower()] = v
            list_objs_as_model.append(self.model(**data_to_lower_key))
        # print(obj.items())
        print(time.time() - time_start)
        return {
            "count": count.scalar(),
            "results": list_objs_as_model,
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
            self.model,
            # Inventry.prod_type, Inventry.rol_profil,
            select(Arinv.name).where(Arinv.autoid == Arinvdet.doc_aid).correlate_except(Arinv).scalar_subquery().label('customer'),
            select(Inventry.prod_type).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('category'),
            select(Inventry.rol_profil).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('profile'),
            select(Inventry.rol_color).where(Inventry.id == Arinvdet.inven).correlate_except(Inventry).scalar_subquery().label('color')
            # literal(Inventry.prod_type).label('category'),
            # select(Inventry.rol_profil).where(Inventry.id == Arinvdet.inven).subquery('INVENTRY'),
            # select(Inventry.prod_type).where(Inventry.id == Arinvdet.inven).subquery('category'),
        ).join(
            self.model.rel_inventry
        # ).join(
        #     self.model.order
        ).where(
            and_(
                self.model.inv_date >= FILTERING_DATA_STARTING_YEAR,
                # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                self.model.par_time == '',
                self.model.category != '',
                self.model.category != 'Vents',
                self.model.inven != None,
                self.model.inven != '',
            ),
        ).options(
            selectinload(self.model.rel_inventry),
            selectinload(self.model.order),
        ).group_by(
            self.model,
            # Inventry.prod_type, Inventry.rol_profil
        )
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query, **kwargs)
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
        query = select(
            self.model,
            select(
                func.count(Arinvdet.doc_aid).label('count_items')
            ).where(
                Arinvdet.doc_aid == self.model.autoid,
                Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
                # Arinvdet.category != None,
                Arinvdet.category != '',
                Arinvdet.category != 'Vents',
                # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                Arinvdet.par_time == '',
                Arinvdet.inven != None,
                Arinvdet.inven != '',
            ).correlate_except(
                Arinvdet
            ).scalar_subquery().label('count_items')
        ).where(
            and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR)
        ).join(
            # sbq, sbq.doc_aid == self.model.autoid
            Arinvdet, and_(
                Arinvdet.doc_aid == self.model.autoid, Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
                # Arinvdet.category != None,
                Arinvdet.category != '',
                Arinvdet.category != 'Vents',
                # Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                Arinvdet.par_time == '',
                Arinvdet.inven != None,
                Arinvdet.inven != '',
            )
        # ).join(
        #     Inventry
        ).options(
            # contains_eager(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
            selectinload(Arinv.details).options(selectinload(Arinvdet.rel_inventry), selectinload(Arinvdet.order)),
        ).group_by(
            self.model,
        )
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query, **kwargs)
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
