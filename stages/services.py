from typing import TypeVar, Generic, Type, Any, Optional, List, Sequence

import sqlalchemy
from fastapi import APIRouter, Depends
from fastapi_restful.cbv import cbv
from pydantic import BaseModel
from sqlalchemy import select, ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from common.models import DefaultBase
from database import get_async_session
from stages.models import Flow, Capacity, Stage, Comment, Item, SalesOrder
from stages.schemas import FlowSchemaIn, CapacitySchemaIn, StageSchemaIn, CommentSchemaIn, ItemSchemaIn, SalesOrderSchemaIn

ModelType = TypeVar("ModelType", bound=DefaultBase)
InputSchemaType = TypeVar("InputSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, InputSchemaType]):
    def __init__(self, model: Type[ModelType], db_session: AsyncSession = Depends(get_async_session)):
        self.model = model
        self.db_session = db_session

    async def get(self, id: int) -> Optional[ModelType | JSONResponse]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db_session.scalars(stmt)
        try:
            return result.one()
        except Exception:
            return JSONResponse(status_code=404, content={"message": f"{self.model.__name__} not found"})

    async def list(self):
        stmt = select(self.model)
        objs: ScalarResult[ModelType] = await self.db_session.scalars(stmt)
        return objs.all()

    async def create(self, obj: InputSchemaType) -> ModelType | JSONResponse:
        stmt = self.model(**obj.model_dump())
        self.db_session.add(stmt)
        try:
            await self.db_session.commit()
            await self.db_session.refresh(stmt)
        except IntegrityError as e:
            return JSONResponse(status_code=400, content={"message": f"{self.model.__name__} did not created {e}"})
        return stmt

    async def update(self, id: int, obj: InputSchemaType) -> Optional[ModelType | JSONResponse]:
        print(locals())
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            return JSONResponse(status_code=404, content={"message": f"{self.model.__name__} not found"})
        for key, value in obj.model_dump().items():
            setattr(instance, key, value)
        try:
            self.db_session.add(instance)
            await self.db_session.commit()
            await self.db_session.refresh(instance)
        except IntegrityError as e:
            return JSONResponse(status_code=400, content={"message": f"Failed to update {self.model.__name__} {e}"})
        return instance

    async def partial_update(self, id: int, obj: dict) -> Optional[ModelType | JSONResponse]:
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            return JSONResponse(status_code=404, content={"message": f"{self.model.__name__} not found"})
        for key, value in obj.items():
            setattr(instance, key, value)
        try:
            self.db_session.add(instance)
            await self.db_session.commit()
            await self.db_session.refresh(instance)
        except IntegrityError as e:
            return JSONResponse(status_code=400, content={"message": f"Failed to update {self.model.__name__} {e}"})
        return instance

    async def delete(self, id: int) -> None | JSONResponse:
        stmt = select(self.model).where(self.model.id == id)
        instance = await self.db_session.scalar(stmt)
        if not instance:
            return JSONResponse(status_code=404, content={"message": f"{self.model.__name__} not found"})
        await self.db_session.delete(instance)
        await self.db_session.commit()
        return JSONResponse(status_code=204, content={"message": f"{self.model.__name__} deleted"})


class CapacitiesService(BaseService[Capacity, CapacitySchemaIn]):
    def __init__(self, model: Type[Capacity] = Capacity, db_session: AsyncSession = Depends(get_async_session)):
        super(CapacitiesService, self).__init__(model=model, db_session=db_session)


class FlowsService(BaseService[Flow, FlowSchemaIn]):
    def __init__(self, model: Type[Flow] = Flow, db_session: AsyncSession = Depends(get_async_session)):
        super(FlowsService, self).__init__(model=model, db_session=db_session)


class StagesService(BaseService[Stage, StageSchemaIn]):
    def __init__(self, model: Type[Stage] = Stage, db_session: AsyncSession = Depends(get_async_session)):
        super(StagesService, self).__init__(model=model, db_session=db_session)


class CommentsService(BaseService[Comment, CommentSchemaIn]):
    def __init__(self, model: Type[Comment] = Comment, db_session: AsyncSession = Depends(get_async_session)):
        super(CommentsService, self).__init__(model=model, db_session=db_session)


class ItemsService(BaseService[Item, ItemSchemaIn]):
    def __init__(self, model: Type[Item] = Item, db_session: AsyncSession = Depends(get_async_session)):
        super(ItemsService, self).__init__(model=model, db_session=db_session)


class SalesOrdersService(BaseService[SalesOrder, SalesOrderSchemaIn]):
    def __init__(self, model: Type[SalesOrder] = SalesOrder, db_session: AsyncSession = Depends(get_async_session)):
        super(SalesOrdersService, self).__init__(model=model, db_session=db_session)
