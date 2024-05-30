import time
from collections import defaultdict
from datetime import datetime
from typing import Generic, Type, Optional, List, NamedTuple

import sqlalchemy
from fastapi import HTTPException
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select, ScalarResult, func, and_, case, Result, Sequence, union_all, literal, text, literal_column, Select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, Query, contains_eager

from common.constants import InputSchemaType, OriginModelType
from common.filters import RenameFieldFilter
from database import get_ebms_session, ebms_engine, get_ebms_engine
from origin_db.filters import CategoryFilter
from origin_db.models import Inprodtype, Arinvdet, Arinv, Inventry
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema, InventrySchema
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


class BaseService(Generic[OriginModelType, InputSchemaType]):
    default_ordering_field = 'recno5'

    def __init__(
            self, model: Type[OriginModelType],
            list_filter: Optional[RenameFieldFilter] = None
    ):
        self.model = model
        self.filter = list_filter

    def to_sql(self, query: Select | Query) -> str:
        return str(query.compile(compile_kwargs={"literal_binds": True}, dialect=sqlalchemy.dialects.mssql.dialect()))

    def dict_keys_to_lowercase(self, obj: dict) -> dict:
        return {k.lower(): v for k, v in obj.items()}

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

    def get_query_for_count(self, **kwargs: Optional[dict]) -> Query:
        query = select(func.count('*')).select_from(self.get_query().subquery())
        return query

    async def get_object_or_404(self, autoid: str) -> OriginModelType:
        obj = await self.get(autoid)
        return obj

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict],) -> dict:
        async with AsyncSession(ebms_engine) as session:
            count = await session.execute(text(self.to_sql(self.get_query_for_count(**kwargs))))
            data = await session.execute(text(self.to_sql(self.get_query(limit=limit, offset=offset, **kwargs))))
        time_start = time.time()
        data_all = data.all()
        list_objs = [data._asdict() for data in data_all]
        list_objs_as_model = []
        for obj in list_objs:
            list_objs_as_model.append(self.model(**self.dict_keys_to_lowercase(obj)))
        print(time.time() - time_start)
        return {
            "count": count.scalar(),
            "results": list_objs_as_model,
        }

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        query = self.get_query().where(self.model.autoid == autoid)
        sql_text = self.to_sql(query)
        async with AsyncSession(ebms_engine) as session:
            result = await session.execute(text(sql_text))
        try:
            result = result.one()
            return self.model(**self.dict_keys_to_lowercase(result._asdict()))
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def list(self, kwargs: Optional[dict] = None) -> Sequence[OriginModelType]:
        async with AsyncSession(ebms_engine) as session:
            objs: ScalarResult[OriginModelType] = await session.scalars(self.get_query())
        return objs.all()

    async def get_listy_by_autoids(self, autoids: List[str] | set) -> Sequence[OriginModelType]:
        async with AsyncSession(ebms_engine) as session:
            objs: ScalarResult[OriginModelType] = await session.scalars(select(self.model).where(self.model.autoid.in_(autoids)))
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
            list_filter: Optional[CategoryFilter] = None
    ):
        super().__init__(model=model, list_filter=list_filter)

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
        async with AsyncSession(ebms_engine) as session:
            result = await session.scalars(smtp)
            try:
                return result.one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {name} not found")


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(
            self, model: Type[Arinvdet] = Arinvdet,
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]):
        query = select(
            self.model,
            Inventry.prod_type.label('category'),
            Inventry.rol_profil.label('profile'),
            Inventry.rol_color.label('color'),
            Arinv.name.label('customer'),
            Arinv.status.label('order_status'),
        ).where(
            and_(
                self.model.inv_date >= FILTERING_DATA_STARTING_YEAR,
                Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                self.model.par_time == '',
                self.model.inven != None,
                self.model.inven != '',
                Arinv.status == 'U'
            ),
        ).join(Arinv, Arinvdet.doc_aid == Arinv.autoid).join(Inventry, Arinvdet.inven == Inventry.id).group_by(
            self.model, Inventry.prod_type, Inventry.rol_profil, Inventry.rol_color, Arinv.name, Arinv.status
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
        sql_text = self.to_sql(stmt)
        async with AsyncSession(ebms_engine) as session:
            objs = await session.execute(text(sql_text))
        return objs.all()

    async def get_origin_item_with_item(self, autoid: str):
        return await self.get(autoid)

    async def get_listy_by_autoids(self, autoids: List[str] | set) -> Sequence[OriginModelType]:
        stmt = self.get_query().where(self.model.autoid.in_(autoids))
        sql_text = self.to_sql(stmt)
        async with AsyncSession(ebms_engine) as session:
            result = await session.execute(text(sql_text))
        list_objs = [self.model(**self.dict_keys_to_lowercase(data._asdict())) for data in result.all()]
        return list_objs


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(
            self, model: Type[Arinv] = Arinv,
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, list_filter=list_filter)

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]):
        query = select(
            self.model,
            select(
                func.count(Arinvdet.doc_aid).label('count_items'),
            ).join(Inventry, Arinvdet.inven == Inventry.id).where(
                Arinvdet.doc_aid == self.model.autoid,
                Arinvdet.inv_date >= FILTERING_DATA_STARTING_YEAR,
                Inventry.prod_type.notin_(LIST_EXCLUDED_PROD_TYPES),
                Arinvdet.par_time == '',
                Arinvdet.inven != None,
                Arinvdet.inven != '',
            ).correlate_except(
                Arinvdet
            ).scalar_subquery().label('count_items')
        ).where(
            and_(
                self.model.inv_date >= FILTERING_DATA_STARTING_YEAR,
                self.model.status == 'U',
            )
        ).group_by(
            self.model,
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

    async def update_ship_date(self, autoids: List[str], ship_date: datetime) -> None:
        stmt = update(self.model).where(self.model.autoid.in_(autoids)).values(ship_date=ship_date)
        async with AsyncSession(ebms_engine) as session:
            await session.execute(stmt)
            await session.commit()

    async def list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        return await self.paginated_list(limit=limit, offset=offset, **kwargs)

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict],) -> dict:
        async with AsyncSession(get_ebms_engine()) as session:
            count = await session.execute(text(self.to_sql(self.get_query_for_count(**kwargs))))
            count = count.scalar()
            data = await session.execute(text(self.to_sql(self.get_query(limit=limit, offset=offset, **kwargs))))
            data_all = data.all()
            list_objs = [self.dict_keys_to_lowercase(data._asdict()) for data in data_all]
            orders_details = await OriginItemService().list_by_orders(autoids=[data['autoid'] for data in list_objs])
        time_start = time.time()
        details = defaultdict(list)
        for order_detail in orders_details:
            order_detail = Arinvdet(**self.dict_keys_to_lowercase(order_detail._asdict()))
            details[order_detail.doc_aid].append(order_detail)
        list_objs_as_model = []
        for obj in list_objs:
            list_objs_as_model.append(self.model(**self.dict_keys_to_lowercase(obj), details=details.get(obj['autoid'], [])))
        print(time.time() - time_start)
        return {
            "count": count,
            "results": list_objs_as_model,
        }

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        query = self.get_query().where(self.model.autoid == autoid)
        sql_text = self.to_sql(query)
        async with AsyncSession(ebms_engine) as session:
            result = await session.execute(text(sql_text))
            details = await OriginItemService().list_by_orders(autoids=[autoid])
        try:
            result = result.one()
            data_details = [Arinvdet(**self.dict_keys_to_lowercase(detail._asdict())) for detail in details]
            order = self.model(**self.dict_keys_to_lowercase(result._asdict()))
            order.details_data = data_details
            return self.model(**self.dict_keys_to_lowercase(result._asdict()), details=data_details)
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def get_origin_order_by_autoids(self, autoids: List[str] | set) -> Sequence[str] | None:
        query = self.get_query().where(self.model.autoid.in_(autoids))
        sql_text = self.to_sql(query)
        async with AsyncSession(ebms_engine) as session:
            result = await session.execute(text(sql_text))
            list_objs = [self.model(**self.dict_keys_to_lowercase(data._asdict())) for data in result.all()]
        return list_objs


class InventryService(BaseService[Inventry, InventrySchema]):
    def __init__(
            self, model: Type[Inventry] = Inventry,
            list_filter: Optional[Filter] = None):
        super().__init__(model=model, list_filter=list_filter)

    async def count_capacity(self, autoids: list[str]) -> Result:
        """  Return total capacity for an inventory group by prod type """
        stmt = select(
            self.model.prod_type.label("prod_type"),
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
        async with AsyncSession(ebms_engine) as session:
            return await session.execute(text(self.to_sql(stmt)))

    async def count_capacity_by_days(self, items_data: dict, list_categories = None) -> Sequence[Result]:
        """  Return total capacity for an inventory group by prod type with count arinv"""
        compair_data = defaultdict(list)
        list_categories = list_categories or []
        for autoid, date in items_data.items():
            compair_data[date.strftime('%Y-%m-%d')].append(autoid)
        list_subqueries = []
        for production_date, autoids in compair_data.items():
            stmt = select(
                self.model.prod_type.label('prod_type'),
                literal(production_date).label("production_date"),
                func.count(Arinvdet.doc_aid).label("count_orders"),
                func.sum(case(
                    (self.model.prod_type == 'Trim', Arinvdet.demd),
                    (Arinvdet.heightd != 0, ((Arinvdet.heightd / 12) * Arinvdet.quan)),
                    else_=Arinvdet.quan
                )).label("total_capacity"),
            ).where(
                Arinvdet.autoid.in_(autoids), Inventry.prod_type.in_(list_categories), Arinvdet.par_time == '',
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
        async with AsyncSession(ebms_engine) as session:
            objs = await session.execute(text(self.to_sql(stmt)))
            result = objs.mappings()
            return result.all()
