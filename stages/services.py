from datetime import date
from typing import TypeVar, Generic, Type, Any, Optional, List, Sequence

import sqlalchemy
from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import select, ScalarResult, func, Integer
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from common.constants import ModelType, InputSchemaType
from common.models import EBMSBase
from database import get_async_session
from origin_db.models import Inprodtype, Arinv, Arinvdet
from stages.models import Flow, Capacity, Stage, Comment, Item, SalesOrder
from stages.schemas import FlowSchemaIn, CapacitySchemaIn, StageSchemaIn, CommentSchemaIn, ItemSchemaIn, SalesOrderSchemaIn


class BaseService(Generic[ModelType, InputSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession = Depends(get_async_session)):
        self.model = model
        self.db_session = db_session

    async def validate_autoid(self, autoid: str, model: EBMSBase):
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

    async def list(self):
        stmt = select(self.model)
        objs: ScalarResult[ModelType] = await self.db_session.scalars(stmt)
        return objs.all()

    async def create(self, obj: InputSchemaType) -> ModelType:
        if getattr(obj, "category_autoid", None) and issubclass(self.model, (Flow, Capacity)):
            await self.validate_autoid(obj.category_autoid, Inprodtype)
        if getattr(obj, "order", None) and issubclass(self.model, (SalesOrder, Item)):
            await self.validate_autoid(obj.order, Arinv)
        if getattr(obj, "origin_item", None) and issubclass(self.model, Item):
            await self.validate_autoid(obj.origin_item, Arinvdet)
        try:
            stmt = self.model(**obj.model_dump())
            self.db_session.add(stmt)
            await self.db_session.commit()
            await self.db_session.refresh(stmt)
        except (IntegrityError, AttributeError) as e:
            raise HTTPException(status_code=400, detail=f"{self.model.__name__} not created {e}")
        return stmt

    async def update(self, id: int, obj: InputSchemaType) -> Optional[ModelType]:
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
    def __init__(self, model: Type[Flow] = Flow, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def list(self):
        stmt = select(self.model).options(selectinload(Flow.stages))
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
    def __init__(self, model: Type[Stage] = Stage, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)


class CommentsService(BaseService[Comment, CommentSchemaIn]):
    def __init__(self, model: Type[Comment] = Comment, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)


class ItemsService(BaseService[Item, ItemSchemaIn]):
    def __init__(self, model: Type[Item] = Item, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def get_autoid_by_production_date(self, production_date: date):
        stmt = select(self.model.origin_item).where(self.model.production_date == production_date)
        objs = await self.db_session.scalars(stmt)
        return objs.all()

    async def get_min_max_production_date(self, autoids: list[str]):
        stmt = select(
            Item.order, func.min(Item.production_date).label("min_date"), func.max(Item.production_date).label("max_date"),
        ).where(Item.order.in_(autoids)).group_by(Item.order)
        objs = await self.db_session.execute(stmt)
        return objs.all()


class SalesOrdersService(BaseService[SalesOrder, SalesOrderSchemaIn]):
    def __init__(self, model: Type[SalesOrder] = SalesOrder, db_session: AsyncSession = Depends(get_async_session)):
        super().__init__(model=model, db_session=db_session)

    async def list_by_orders(self, autoids: list[str]):
        stmt = select(SalesOrder).where(SalesOrder.order.in_(autoids))
        objs = await self.db_session.scalars(stmt)
        return objs.all()
