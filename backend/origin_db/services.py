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
from database import get_ebms_session, ebms_engine, get_ebms_engine, ebms_session_maker
from origin_db.filters import CategoryFilter
from origin_db.models import Inprodtype, Arinvdet, Arinv, Inventry
from origin_db.schemas import CategorySchema, ArinvDetSchema, ArinvRelatedArinvDetSchema, InventrySchema
from settings import FILTERING_DATA_STARTING_YEAR, LIST_EXCLUDED_PROD_TYPES


class BaseService(Generic[OriginModelType, InputSchemaType]):
    default_ordering_field = 'recno5'

    def __init__(
            self, model: Type[OriginModelType],
            list_filter: Optional[RenameFieldFilter] = None,
            db_session: Optional[AsyncSession] = None
    ):
        self.model = model
        self.filter = list_filter
        self.db_session = db_session

    async def check_autoids_exist(self, autoid: [str]) -> None:
        query = await self.get_query()
        query = query.where(self.model.autoid == autoid)
        sql_text = await self.to_sql(query)
        async with ebms_session_maker.begin() as session:
            obj = await session.scalars(text(sql_text))
            try:
                result = obj.one()
            except NoResultFound:
                raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")
            return result

    async def to_sql(self, query: Select | Query) -> str:
        return str(query.compile(compile_kwargs={"literal_binds": True}, dialect=sqlalchemy.dialects.mssql.dialect()))

    def dict_keys_to_lowercase(self, obj: dict) -> dict:
        return {k.lower(): v for k, v in obj.items()}

    async def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
        query = select(self.model).where(and_(self.model.inv_date >= FILTERING_DATA_STARTING_YEAR))
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def get_query_for_count(self, **kwargs: Optional[dict]) -> Query:
        query = await self.get_query(**kwargs)
        query = query.order_by(None).alias()
        query = select(func.count('*')).select_from(query)
        return query

    async def get_object_or_404(self, autoid: str) -> OriginModelType:
        obj = await self.get(autoid)
        return obj

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict],) -> dict:

        count = await self.db_session.execute(await self.to_sql(await self.get_query_for_count(**kwargs)))
        count = await count.fetchone()
        query = await self.to_sql(await self.get_query(limit=limit, offset=offset, **kwargs))
        data = await self.db_session.execute(await self.to_sql(await self.get_query(limit=limit, offset=offset, **kwargs)))
        time_start = time.time()
        data_all = await data.fetchall()
        columns = [column[0].lower() for column in data.description]
        list_objs = [dict(zip(columns, data)) for data in data_all]
        list_objs_as_model = []
        for obj in list_objs:
            list_objs_as_model.append(self.model(**obj))
        print(time.time() - time_start)
        return {
            "count": count[0],
            "results": list_objs_as_model,
        }

    async def get_with_sqlalchemy(self, autoid: str) -> Optional[OriginModelType]:
        query = await self.get_query()
        query = query.where(self.model.autoid == autoid)
        sql_text = await self.to_sql(query)
        async with ebms_session_maker() as session:
            result = await session.execute(text(sql_text))
        try:
            result = result.one()
            return self.model(**self.dict_keys_to_lowercase(result._asdict()))
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        if not self.db_session:
            return await self.get_with_sqlalchemy(autoid)
        query = await self.get_query()
        query = query.where(self.model.autoid == autoid)
        sql_text = await self.to_sql(query)
        result = await self.db_session.execute(sql_text)
        columns = [column[0].lower() for column in result.description]
        try:
            result = result.one()
            return self.model(**zip(columns, result))
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def list(self, kwargs: Optional[dict] = None) -> Sequence[OriginModelType]:
        query = await self.get_query()
        objs: ScalarResult[OriginModelType] = await self.db_session.execute(await self.to_sql(query))
        columns = [column[0].lower() for column in objs.description]
        objs = await objs.fetchall()
        list_objs = [self.model(**dict(zip(columns, data))) for data in objs]
        return list_objs

    async def get_listy_by_autoids(self, autoids: List[str] | set) -> Sequence[OriginModelType]:
            query = await self.to_sql(select(self.model).where(self.model.autoid.in_(autoids)))
            objs: ScalarResult[OriginModelType] = await self.db_session.execute(query)
            columns = [column[0].lower() for column in objs.description]
            objs = await objs.fetchall()
            list_objs = [dict(zip(columns, data)) for data in objs]
            return list_objs

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
            list_filter: Optional[CategoryFilter] = None,
            db_session: Optional[AsyncSession] = None
    ):
        super().__init__(model=model, list_filter=list_filter, db_session=db_session)

    async def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
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
        smtp = await self.get_query()
        smtp = smtp.where(self.model.prod_type == name)
        result = await self.db_session.execute(await self.to_sql(smtp))
        obj = await result.fetchone()
        columns = [column[0].lower() for column in result.description]
        obj = dict(zip(columns, obj))
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {name} not found")
        return self.model(**obj)


class OriginItemService(BaseService[Arinvdet, ArinvDetSchema]):
    def __init__(
            self, model: Type[Arinvdet] = Arinvdet,
            list_filter: Optional[Filter] = None,
            db_session: Optional[AsyncSession] = None
    ):
        super().__init__(model=model, list_filter=list_filter, db_session=db_session)

    async def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
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
        query = await self.get_query()
        stmt = query.where(self.model.doc_aid.in_(autoids))
        objs = await self.db_session.execute(await self.to_sql(stmt))
        columns = [column[0].lower() for column in objs.description]
        objs = await objs.fetchall()
        list_objs = [self.model(**dict(zip(columns, data))) for data in objs]
        return list_objs

    async def list_by_orders_with_sqlalchemy(self, autoids: List[str]):
        stmt = await self.get_query()
        stmt = stmt.where(self.model.doc_aid.in_(autoids))
        sql_text = await self.to_sql(stmt)
        async with ebms_session_maker() as session:
            objs = await session.execute(text(sql_text))
        return objs.all()

    async def get_origin_item_with_item(self, autoid: str):
        return await self.get_with_sqlalchemy(autoid)

    async def get_list_by_autoids_with_sqlalchemy(self, autoids: List[str] | set) -> Sequence[OriginModelType]:
        stmt = await self.get_query()
        stmt = stmt.where(self.model.autoid.in_(autoids))
        sql_text = await self.to_sql(stmt)
        async with ebms_session_maker() as session:
            result = await session.execute(text(sql_text))
        list_objs = [self.model(**self.dict_keys_to_lowercase(data._asdict())) for data in result.all()]
        return list_objs

    async def get_listy_by_autoids(self, autoids: List[str] | set) -> Sequence[OriginModelType]:
        if not self.db_session:
            return await self.get_list_by_autoids_with_sqlalchemy(autoids)
        stmt = await self.get_query()
        stmt = stmt.where(self.model.autoid.in_(autoids))
        result = await self.db_session.execute(await self.to_sql(stmt))
        columns = [column[0].lower() for column in result.description]
        objs = await result.fetchall()
        list_objs = [self.model(**dict(zip(columns, data))) for data in objs]
        return list_objs


class OriginOrderService(BaseService[Arinv, ArinvRelatedArinvDetSchema]):
    def __init__(
            self, model: Type[Arinv] = Arinv,
            list_filter: Optional[Filter] = None,
            db_session: Optional[AsyncSession] = None

    ):
        super().__init__(model=model, list_filter=list_filter, db_session=db_session)

    async def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
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
        async with ebms_session_maker.begin() as session:
            await session.execute(stmt)
            await session.commit()

    async def list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        return await self.paginated_list(limit=limit, offset=offset, **kwargs)

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict],) -> dict:
        # async with ebms_session_maker.begin() as session:
        start_time = time.time()
        count = await self.db_session.execute(await self.to_sql(await self.get_query_for_count(**kwargs)))
        count = await count.fetchone()
        query = await self.to_sql(await self.get_query(limit=limit, offset=offset, **kwargs))
        data = await self.db_session.execute(query)
        data_all = await data.fetchall()

        columns = [column[0].lower() for column in data.description]
        list_objs = [dict(zip(columns, data)) for data in data_all]
        print("get orders as dict", time.time() - start_time)
        orders_details = await OriginItemService(db_session=self.db_session).list_by_orders(autoids=[data['autoid'] for data in list_objs])
        print("get orders details", time.time() - start_time)
        time_start = time.time()
        details = defaultdict(list)
        for order_detail in orders_details:
            details[order_detail.doc_aid].append(order_detail)
        list_objs_as_model = []
        for obj in list_objs:
            list_objs_as_model.append(self.model(**self.dict_keys_to_lowercase(obj), details=details.get(obj['autoid'], [])))
        print(time.time() - time_start)
        return {
            "count": count[0],
            "results": list_objs_as_model,
        }

    async def get_with_sqlalchemy(self, autoid: str) -> Optional[OriginModelType]:
        print(f"get_by_sqlalchemy {autoid}")
        query = await self.get_query()
        query = query.where(self.model.autoid == autoid)
        sql_text = await self.to_sql(query)
        async with ebms_session_maker() as session:
            result = await session.execute(text(sql_text))
            print(result)
            details = await OriginItemService().list_by_orders_with_sqlalchemy(autoids=[autoid])
        try:
            result = result.one()
            data_details = [Arinvdet(**self.dict_keys_to_lowercase(detail._asdict())) for detail in details]
            print(data_details)
            order = self.model(**self.dict_keys_to_lowercase(result._asdict()))
            order.details_data = data_details
            return self.model(**self.dict_keys_to_lowercase(result._asdict()), details=data_details)
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def get_origin_order_by_autoids_with_sqlalchemy(self, autoids: List[str] | set) -> Sequence[str] | None:
        query = await self.get_query()
        query = query.where(self.model.autoid.in_(autoids))
        sql_text = await self.to_sql(query)
        async with ebms_session_maker() as session:
            result = await session.execute(text(sql_text))
            list_objs = [self.model(**self.dict_keys_to_lowercase(data._asdict())) for data in result.all()]
        return list_objs

    async def get(self, autoid: str) -> Optional[OriginModelType]:
        if self.db_session is None:
            return await self.get_with_sqlalchemy(autoid)
        print(self.db_session)
        query = await self.get_query()
        query = query.where(self.model.autoid == autoid)
        sql_text = await self.to_sql(query)
        result = await self.db_session.execute(sql_text)
        obj = await result.fetchone()
        if not obj:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")
        columns = [column[0].lower() for column in result.description]

        details = await OriginItemService(db_session=self.db_session).list_by_orders(autoids=[autoid])
        try:

            result = dict(zip(columns, obj))
            data_details = details
            return self.model(**result, details=data_details)
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {autoid} not found")

    async def get_origin_order_by_autoids(self, autoids: List[str] | set) -> Sequence[str] | None:
        query = await self.get_query()
        query = query.where(self.model.autoid.in_(autoids))
        sql_text = await self.to_sql(query)
        result = await self.db_session.execute(text(sql_text))
        objs = await result.fetchall()
        columns = [column[0].lower() for column in result.description]
        list_objs = [self.model(**dict(zip(columns, obj))) for obj in objs]
        return list_objs


class InventryService(BaseService[Inventry, InventrySchema]):
    def __init__(
            self, model: Type[Inventry] = Inventry,
            list_filter: Optional[Filter] = None,
            db_session: Optional[AsyncSession] = None
    ):
        super().__init__(model=model, list_filter=list_filter, db_session=db_session)

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
        async with ebms_session_maker.begin() as session:
            return await session.execute(text(await self.to_sql(stmt)))

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
        result = await self.db_session.execute(await self.to_sql(stmt))
        objs = await result.fetchall()
        columns = [column[0].lower() for column in result.description]
        result = [dict(zip(columns, obj)) for obj in objs]
        return result
