import calendar
from datetime import date, datetime
from typing import TypeVar, Generic, Type, Any, Optional, List, Sequence, Iterable

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
from stages.schemas import (
    FlowSchemaIn, CapacitySchemaIn, StageSchemaIn, CommentSchemaIn, ItemSchemaIn, SalesOrderSchemaIn, MultiUpdateItemSchema,
    MultiUpdateSalesOrderSchema
)


class BaseService(Generic[ModelType, InputSchemaType]):
    def __init__(
            self, model: Type[ModelType], db_session: AsyncSession = Depends(get_async_session),
            list_filter: Optional[RenameFieldFilter] = None
    ):
        self.model = model
        self.db_session = db_session
        self.filter = list_filter

    async def add_all(self, instances: Iterable[object], doing='update') -> None:
        try:
            self.db_session.add_all(instances)
            await self.db_session.commit()
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail=f"Failed to {doing} {self.model.__name__} {e}")

    async def root_validator(self, obj: InputSchemaType) -> InputSchemaType:
        if getattr(obj, "category_autoid", None) and issubclass(self.model, (Flow, Capacity)):
            await self.validate_autoid(obj.category_autoid, Inprodtype)
        if getattr(obj, "order", None) and issubclass(self.model, (SalesOrder, Item)):
            await self.validate_autoid(obj.order, Arinv)
        if getattr(obj, "origin_item", None) and issubclass(self.model, Item):
            await self.validate_autoid(obj.origin_item, Arinvdet)
        if data := getattr(obj, "production_date", None):
            await self.validate_production_date(data)
        return obj

    async def validate_instance(self, instance: ModelType, input_obj: InputSchemaType) -> tuple[ModelType, InputSchemaType]:
        return instance, input_obj

    async def validate_production_date(self, production_date: date):
        company_working_weekend = await self.db_session.scalars(select(CompanyProfile))
        company_working_weekend = company_working_weekend.first()
        company_working_weekend = company_working_weekend.working_weekend if company_working_weekend else False
        if not company_working_weekend and production_date.isoweekday() > 5:
            raise HTTPException(status_code=400, detail="Production date cannot be on a weekend")
        return production_date

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
        query = select(self.model)
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
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

    async def count_query_objs(self, query) -> int:
        return await self.db_session.scalar(select(func.count()).select_from(query.subquery()))

    async def paginated_list(self, limit: int = 10, offset: int = 0, **kwargs: Optional[dict]) -> dict:
        count = await self.count_query_objs(self.get_query())
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query(limit=limit, offset=offset, **kwargs))
        return {
            "count": count,
            "results": objs.all(),
        }

    async def get(self, id: int) -> Optional[ModelType]:
        stmt = self.get_query().where(self.model.id == id)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except NoResultFound:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")

    async def list(self, **kwargs: Optional[dict]) -> Sequence[OriginModelType]:
        objs: ScalarResult[OriginModelType] = await self.db_session.scalars(self.get_query(**kwargs))
        return objs.all()

    async def get_filtering_origin_items_autoids(self) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.origin_item))
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all() or ['-1']
        return None

    async def get_filtering_origin_orders_autoids(self, **kwargs) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.order), **kwargs)
            objs: ScalarResult[str] = await self.db_session.scalars(query)
            return objs.all() or ['-1']
        return None

    async def create(self, obj: InputSchemaType) -> ModelType:
        obj = await self.root_validator(obj)
        try:
            stmt = self.model(**obj.model_dump(exclude_none=True, exclude_unset=True))
            self.db_session.add(stmt)
            await self.db_session.commit()
            await self.db_session.refresh(stmt)
        except (IntegrityError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=f"{self.model.__name__} not created {e}")
        return stmt

    async def update(self, id: int, obj: InputSchemaType) -> Optional[ModelType]:
        obj = await self.root_validator(obj)
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        await self.validate_instance(instance, obj)
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
        baseschema = type('BaseModel', (), obj)
        await self.root_validator(baseschema)
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with id {id} not found")
        await self.validate_instance(instance, baseschema)
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

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
        query = select(self.model).options(selectinload(Flow.stages))
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def create(self, obj: InputSchemaType) -> Optional[ModelType]:
        new_flow = await super().create(obj)
        stmt = select(Stage).where(and_(Stage.default == True, Stage.flow_id == None))
        default_stages = await self.db_session.scalars(stmt)
        created_stages = []
        for stage in default_stages.all():
            stage.flow_id = new_flow.id
            stage.default = False
            created_stages.append(stage)
        self.db_session.add_all(created_stages)
        await self.db_session.commit()
        await self.db_session.refresh(new_flow)
        return new_flow

    async def list(self, **kwargs: Optional[dict]) -> Sequence[ModelType]:
        stmt = select(self.model).options(selectinload(Flow.stages))
        if self.filter:
            stmt = self.filter.filter(stmt, **kwargs)
            stmt = stmt.order_by(self.model.id)
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

    async def validate_instance(self, instance: Item, input_obj: ItemSchemaIn) -> tuple[Item, ItemSchemaIn]:
        if input_obj.stage_id:
            stmt = select(Stage).where(Stage.id == input_obj.stage_id, Stage.flow_id == instance.flow_id)
            stage = await self.db_session.scalar(stmt)
            if not stage:
                raise HTTPException(status_code=404, detail=f"Stage with id {input_obj.stage_id}  and flow {instance.flow_id} not found")
            instance.stage = stage
        return instance, input_obj

    def get_query(self, limit: int = None, offset: int = None, **kwargs: Optional[dict]) -> Query:
        query = select(self.model).options(
            selectinload(self.model.stage),
            selectinload(self.model.comments),
            selectinload(self.model.flow).selectinload(Flow.stages),
        )
        if self.filter:
            query = self.filter.filter(query, **kwargs)
            query = self.filter.sort(query)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    async def multiupdate(self, obj: MultiUpdateItemSchema) -> Optional[MultiUpdateItemSchema]:
        object_data = obj.model_dump(exclude_unset=True)
        origin_items = set(object_data.pop("origin_items", []))
        if production_date := object_data.get("production_date"):
            await self.validate_production_date(production_date)
        category = None
        if flow_id := object_data.get("flow_id"):
            flow = await self.db_session.scalar(select(Flow).where(Flow.id == flow_id))
            if not flow:
                raise HTTPException(status_code=404, detail=f"Flow with id {flow_id} not found")
            category = await self.db_session.scalar(select(Inprodtype).where(Inprodtype.autoid == flow.category_autoid))
            category = category.prod_type if category else False
        origin_items_objs = await self.db_session.scalars(
            select(Arinvdet).where(Arinvdet.autoid.in_(origin_items)).options(selectinload(Arinvdet.rel_inventry))
        )
        stage = None
        if stage_id := object_data.get("stage_id"):
            stage = await self.db_session.scalar(select(Stage).where(Stage.id == stage_id).options(selectinload(Stage.flow)))
            if not stage:
                raise HTTPException(status_code=404, detail=f"Stage with id {stage_id} not found")
            flow_id = stage.flow_id
            category = await self.db_session.scalar(select(Inprodtype).where(Inprodtype.autoid == stage.flow.category_autoid))
            category = category.prod_type if category else False
        origin_items_data = {item.autoid: item for item in origin_items_objs}
        stmt = select(self.model).where(self.model.origin_item.in_(origin_items))
        objs = await self.db_session.scalars(stmt)
        existing_items = set()
        items = objs.all()
        for item in items:
            origin_item = origin_items_data.pop(item.origin_item, None)
            if not origin_item:
                continue
            if flow_id and category is not None:
                if origin_item.category != category:
                    raise HTTPException(
                        status_code=400, detail=f"Cannot update item {item.origin_item} with flow {flow_id} and category {category}"
                    )
            if stage_id and item.flow_id != stage.flow_id:
                raise HTTPException(
                    status_code=400, detail=f"Cannot update item {item.origin_item} with stage {stage_id} and flow {item.flow_id}"
                )
            for key, value in object_data.items():
                setattr(item, key, value)
            existing_items.add(item.origin_item)
        await self.add_all(items)
        created_items = []
        for origin_item in origin_items_data.values():
            if flow_id and category is not None:
                if origin_item.category != category:
                    raise HTTPException(
                        status_code=400, detail=f"Cannot update item {origin_item.autoid} with flow {flow_id} and category {category}"
                    )
            if stage_id and stage:
                object_data["flow_id"] = stage.flow_id
            created_items.append(Item(origin_item=origin_item.autoid, order=origin_item.doc_aid, **object_data))
        if created_items:
            await self.add_all(created_items)
        return obj

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
        # print(787887878778878)
        # subq = select(Item.order).where(
        #     and_(
        #         Item.order.in_(autoids),
        #         Item.production_date != None,
        #         Item.stage_id != None,
        #         Stage.name == "Done",
        #     )
        # ).join(Stage)
        # print('sffwefwwefwwefwwefwwef')
        # stmt = select(
        #     Item.order, func.min(Item.production_date).label("min_date"), func.max(Item.production_date).label("max_date"),
        #     case((subq.exists(), 1), else_=0).label("completed"),
        # ).where(self.model.order.in_(autoids)).group_by(Item.order, Item.production_date, Stage.name)
        # print('sffwefwwefwwefwwefwwef')
        # objs = await self.db_session.execute(stmt)
        subq = case((and_(
            self.model.production_date != None,
            # Stage.name == "Done",
        ), 1), else_=0).label("completed")
        stmt = select(
            self.model.order,
            subq,
        ).where(self.model.order.in_(autoids)).join(Stage).group_by(self.model.order, self.model.production_date, Stage.name)
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

    async def list(self, **kwargs: Optional[dict]) -> Sequence[ModelType]:
        stmt = select(self.model).options(
            selectinload(self.model.stage),
            selectinload(self.model.comments),
            selectinload(self.model.flow).selectinload(Flow.stages),
        )
        if self.filter:
            stmt = self.filter.filter(stmt, **kwargs)
            stmt = self.filter.sort(stmt)
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

    async def get_filtering_origin_orders_autoids(self, do_ordering: bool = False) -> Sequence[str] | None:
        if self.filter and self.filter.is_filtering_values:
            query = self.filter.filter(select(self.model.order))
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

    async def multiupdate(self, objs: MultiUpdateSalesOrderSchema):
        object_data = objs.model_dump(exclude_unset=True)
        origin_orders = set(object_data.pop("origin_orders", []))
        if production_date := object_data.get("production_date"):
            await self.validate_production_date(production_date)
        sales_orders = await self.db_session.scalars(select(self.model).where(self.model.order.in_(origin_orders)))
        origin_orders = await self.db_session.scalars(select(Arinv).where(Arinv.autoid.in_(origin_orders)))
        origin_orders_data = {obj.autoid: obj for obj in origin_orders}
        for obj in sales_orders:
            origin_order = origin_orders_data.pop(obj.order, None)
            for k, v in object_data.items():
                setattr(obj, k, v)
        await self.add_all(sales_orders)
        if origin_orders_data:
            new_sales_orders = []
            for obj in origin_orders_data.values():
                new_sales_orders.append(SalesOrder(order=obj.autoid, **object_data))
            await self.add_all(new_sales_orders)
        return objs

    async def list_by_orders(self, autoids: list[str]):
        stmt = select(self.model).where(self.model.order.in_(autoids))
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_filtering_origin_orders_autoids(self, do_ordering: bool = False) -> Sequence[str] | None:
        # subq = select(self.model.order).where(
        #     and_(
        #         self.model.production_date != None,
        #         self.model.stage_id != None,
        #         Stage.name == "Done",
        #     )
        # ).join(Stage)
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
