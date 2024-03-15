import calendar
from datetime import date, datetime
from typing import TypeVar, Generic, Type, Any, Optional, List, Sequence

import sqlalchemy
from fastapi import APIRouter, Depends
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import select, ScalarResult, func, Integer, case, or_, and_, Result
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload, Query
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from common.constants import ModelType, InputSchemaType, OriginModelType
from common.filters import RenameFieldFilter
from common.models import EBMSBase
from database import get_async_session
from origin_db.models import Inprodtype, Arinv, Arinvdet
from profiles.models import CompanyProfile
from stages.models import Flow, Capacity, Stage, Comment, Item, SalesOrder
from stages.schemas import FlowSchemaIn, CapacitySchemaIn, StageSchemaIn, CommentSchemaIn, ItemSchemaIn, SalesOrderSchemaIn


class BaseService(Generic[ModelType, InputSchemaType]):
    def __init__(
            self, model: Type[ModelType], db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[RenameFieldFilter] = None
    ):
        self.model = model
        self.db_session = db_session
        self.filter = list_filter

    async def validate_production_date(self, production_date: date):
        company_working_weekend = await self.db_session.scalars(select(CompanyProfile))
        company_working_weekend = company_working_weekend.first()
        if company_working_weekend:
            company_working_weekend = company_working_weekend.working_weekend
        else:
            company_working_weekend = False
        if not company_working_weekend and production_date.isoweekday() > 5:
            raise HTTPException(status_code=400, detail="Production date cannot be on a weekend")
        return production_date

    def get_query(self, limit: int = None, offset: int = None) -> Query:
        query = select(self.model)
        if self.filter:
            query = self.filter.filter(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def validate_autoid(self, autoid: str, model):
        smt = select(model).where(model.autoid == autoid)
        result = await self.db_session.scalar(smt)
        if not result:
            raise HTTPException(status_code=404, detail=f"{model.__name__} with autoid {autoid} not found")

    async def get(self, id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")

    async def paginated_list(self, limit: int = 10, offset: int = 0):
        objs: ScalarResult[ModelType] = await self.db_session.scalars(self.get_query(limit=limit, offset=offset))
        return objs.all()

    async def list(self):
        query = self.get_query()
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(query)
        objs = await self.db_session.scalars(query)
        return objs.all()

    async def get_filtering_origin_items_autoids(self) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.origin_item))
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all() or ['-1']
        return None

    async def create(self, obj: InputSchemaType) -> ModelType:
        if getattr(obj, "category_autoid", None) and issubclass(self.model, (Flow, Capacity)):
            await self.validate_autoid(obj.category_autoid, Inprodtype)
        if getattr(obj, "order", None) and issubclass(self.model, (SalesOrder, Item)):
            await self.validate_autoid(obj.order, Arinv)
        if getattr(obj, "origin_item", None) and issubclass(self.model, Item):
            await self.validate_autoid(obj.origin_item, Arinvdet)
        if data := getattr(obj, "production_date", None):
            await self.validate_production_date(data)
        try:
            stmt = self.model(**obj.model_dump(exclude_none=True, exclude_unset=True))
            self.db_session.add(stmt)
            await self.db_session.commit()
            await self.db_session.refresh(stmt)
        except (IntegrityError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=f"{self.model.__name__} not created {e}")
        return stmt

    async def update(self, id: int, obj: InputSchemaType) -> Optional[ModelType]:
        if data := getattr(obj, "production_date", None):
            await self.validate_production_date(data)
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        for key, value in obj.model_dump().items():
            setattr(instance, key, value)
        try:
            self.db_session.add(instance)
            await self.db_session.commit()
            await self.db_session.refresh(instance)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Failed to update {self.model.__name__} {e}")
        return instance

    async def partial_update(self, id: int, obj: dict) -> Optional[ModelType]:
        if data := obj.get("production_date", None):
            await self.validate_production_date(data)
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        for key, value in obj.items():
            setattr(instance, key, value)
        try:
            self.db_session.add(instance)
            await self.db_session.commit()
            await self.db_session.refresh(instance)
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Failed to update {self.model.__name__} {e}")
        return instance

    async def delete(self, id: int) -> None | JSONResponse:
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        await self.db_session.delete(instance)
        await self.db_session.commit()
        return JSONResponse(status_code=204, content={"message": f"{self.model.__name__} with id {id} deleted"})


class CapacitiesService(BaseService[Capacity, CapacitySchemaIn]):
    def __init__(self, model: Type[Capacity] = Capacity, db_session: AsyncSession = Depends(get_async_session)):
        super(CapacitiesService, self).__init__(model=model, db_session=db_session)


class FlowsService(BaseService[Flow, FlowSchemaIn]):
    def __init__(
            self, model: Type[Flow] = Flow, db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    async def list(self):
        stmt = select(self.model).options(selectinload(Flow.stages))
        if self.filter:
            stmt = self.filter.filter(stmt)
        objs: ScalarResult[ModelType] = await self.db_session.scalars(stmt)
        return objs.all()

    async def group_by_category(self) -> dict:
        flows = await self.db_session.execute(
            select(
                func.count(Flow.category_autoid).cast(Integer).label("flow_count"), Flow.category_autoid
            ).group_by(Flow.category_autoid)
        )
        flows = flows.all()
        return {flow.category_autoid: flow.flow_count for flow in flows}


class StagesService(BaseService[Stage, StageSchemaIn]):
    def __init__(
            self, model: Type[Stage] = Stage, db_session: AsyncSession = Depends(get_async_session), list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)


class CommentsService(BaseService[Comment, CommentSchemaIn]):
    def __init__(
            self, model: Type[Comment] = Comment, db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)


class ItemsService(BaseService[Item, ItemSchemaIn]):
    def __init__(
            self, model: Type[Item] = Item, db_session: AsyncSession = Depends(get_async_session), list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    async def get_autoid_by_production_date(self, production_date: str | None):
        production_date = datetime.strptime(production_date, "%Y-%m-%d") if production_date else date.today()
        stmt = select(self.model.origin_item).where(and_(func.date(self.model.production_date) == production_date))
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_autoids_and_production_date_by_month(self, year: int, month: int):
        list_of_days = [datetime(year, month, day).strftime('%Y-%m-%d') for day in range(1, calendar.monthrange(year, month)[1] + 1)]
        min_date = min(list_of_days)
        max_date = max(list_of_days)
        stmt = select(self.model).where(
            and_(
                func.date(self.model.production_date) >= datetime.strptime(min_date, "%Y-%m-%d"),
                func.date(self.model.production_date) <= datetime.strptime(max_date, "%Y-%m-%d")
            )
        )
        objs = await self.db_session.scalars(stmt)
        result = objs.all()
        return result

    async def group_by_item_statistics(self, autoids: list[str]):
        """
            Returns annotated:
                - completed
        """
        subq = case((and_(
            self.model.production_date != None,
            Stage.name == "Done",
        ), 1), else_=0).label("completed")
        stmt = select(
            self.model.origin_item,
            subq,
        ).where(self.model.origin_item.in_(autoids)).join(Stage).group_by(self.model.origin_item, self.model.production_date, Stage.name)
        objs = await self.db_session.execute(stmt)
        return objs.all()

    async def group_by_order_annotated_statistics(self, autoids: list[str]):
        """
            Returns annotated:
                - completed
                - min_date
                - max_date
        """
        subq = select(self.model.order).where(
            and_(
                self.model.order.in_(autoids),
                self.model.production_date != None,
                self.model.stage_id != None,
                Stage.name == "Done",
            )
        ).join(Stage)
        stmt = select(
            self.model.order, func.min(Item.production_date).label("min_date"), func.max(Item.production_date).label("max_date"),
            case((subq.exists(), 1), else_=0).label("completed"),
        ).where(Item.order.in_(autoids)).group_by(Item.order)
        objs = await self.db_session.execute(stmt)
        return objs.all()

    async def get_related_items_by_order(self, autoids: list[str]):
        stmt = select(self.model).where(self.model.order.in_(autoids)).options(
            selectinload(self.model.stage),
            selectinload(self.model.comments),
            selectinload(self.model.flow).selectinload(Flow.stages),
        )
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_related_items_by_origin_items(self, autoids: list[str]):
        stmt = select(self.model).where(self.model.origin_item.in_(autoids)).options(
            selectinload(self.model.stage),
            selectinload(self.model.comments),
            selectinload(self.model.flow).selectinload(Flow.stages),
        )
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def list(self):
        stmt = select(self.model).options(
            selectinload(self.model.stage),
            selectinload(self.model.comments),
            selectinload(self.model.flow).selectinload(Flow.stages),
        )
        if self.filter:
            stmt = self.filter.filter(stmt)
        objs: ScalarResult[ModelType] = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_filtering_origin_items_autoids(self, do_ordering: bool = False) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.origin_item))
            query = self.filter.sort(query)
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all() or ['-1']
        if do_ordering:
            query = self.filter.sort(select(self.model.origin_item))
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all()
        return None


class SalesOrdersService(BaseService[SalesOrder, SalesOrderSchemaIn]):
    def __init__(
            self, model: Type[SalesOrder] = SalesOrder, db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[Filter] = None
    ):
        super().__init__(model=model, db_session=db_session, list_filter=list_filter)

    async def list_by_orders(self, autoids: list[str]):
        stmt = select(self.model).where(self.model.order.in_(autoids))
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_filtering_origin_orders_autoids(self, do_ordering: bool = False) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.order))
            query = self.filter.sort(query)
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all() or ['-1']
        if do_ordering:
            query = self.filter.sort(select(self.model.order))
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all()
        return None
