from fastapi import Depends, APIRouter
from fastapi_pagination import LimitOffsetPage, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from stages.services import CapacitiesService, StagesService, FlowsService, CommentsService, ItemsService, SalesOrdersService
from stages.schemas import (
    CapacitySchema, CapacitySchemaIn, StageSchema, StageSchemaIn, CommentSchemaIn, CommentSchema, ItemSchema, ItemSchemaIn,
    SalesOrderSchema, SalesOrderSchemaIn, FlowSchema, FlowSchemaIn, FlowSchemaOut, ItemSchemaOut
)


router = APIRouter()


@router.post("/capacities/", response_model=CapacitySchema, tags=["capacity"])
async def create_capacity(store: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await CapacitiesService(db_session=session).create(store)


@router.get("/capacities/", tags=["capacity"], response_model=LimitOffsetPage[CapacitySchema])
async def get_capacities(session: AsyncSession = Depends(get_async_session)):
    result = await CapacitiesService(db_session=session).list()
    return paginate(result)


@router.get("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def get_capacity(id: int, session: AsyncSession = Depends(get_async_session)):
    return await CapacitiesService(db_session=session).get(id)


@router.put("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def update_capacity(id: int, capacity: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await CapacitiesService(db_session=session).update(id, capacity)


@router.patch("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def partial_update_capacity(id: int, capacity: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session)):
    capacity = capacity.model_dump(exclude_unset=True)
    return await CapacitiesService(db_session=session).partial_update(id, capacity)


@router.delete("/capacities/{id}/", tags=["capacity"])
async def delete_capacity(id: int, session: AsyncSession = Depends(get_async_session)):
    return await CapacitiesService(db_session=session).delete(id)


@router.get("/stages/", tags=["stage"], response_model=LimitOffsetPage[StageSchema])
async def get_stages(session: AsyncSession = Depends(get_async_session)):
    result = await StagesService(db_session=session).list()
    return paginate(result)


@router.get("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def get_stage(id: int, session: AsyncSession = Depends(get_async_session)):
    return await StagesService(db_session=session).get(id)


@router.post("/stages/", tags=["stage"], response_model=StageSchema)
async def create_stage(stage: StageSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await StagesService(db_session=session).create(stage)


@router.put("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def update_stage(id: int, stage: StageSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await StagesService(db_session=session).update(id, stage)


@router.patch("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def partial_update_stage(id: int, data: StageSchemaIn, session: AsyncSession = Depends(get_async_session)):
    stage = data.model_dump(exclude_unset=True)
    print(stage)
    return await StagesService(db_session=session).partial_update(id, stage)


@router.delete("/stages/{id}/", tags=["stage"])
async def delete_stage(id: int, session: AsyncSession = Depends(get_async_session)):
    return await StagesService(db_session=session).delete(id)


@router.get("/comments/", tags=["comments"], response_model=LimitOffsetPage[CommentSchema])
async def get_comments(session: AsyncSession = Depends(get_async_session)):
    result = await CommentsService(db_session=session).list()
    return paginate(result)


@router.get("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def get_comment(id: int, session: AsyncSession = Depends(get_async_session)):
    return await CommentsService(db_session=session).get(id)


@router.post("/comments/", tags=["comments"], response_model=CommentSchema)
async def create_comment(comment: CommentSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await CommentsService(db_session=session).create(comment)


@router.put("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def update_comment(id: int, comment: CommentSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await CommentsService(db_session=session).update(id, comment)


@router.patch("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def partial_update_comment(id: int, comment: CommentSchemaIn, session: AsyncSession = Depends(get_async_session)):
    comment = comment.model_dump(exclude_unset=True)
    return await CommentsService(db_session=session).partial_update(id, comment)


@router.delete("/comments/{id}/", tags=["comments"])
async def delete_comment(id: int, session: AsyncSession = Depends(get_async_session)):
    return await CommentsService(db_session=session).delete(id)


@router.get("/items/", tags=["items"], response_model=LimitOffsetPage[ItemSchema])
async def get_items(session: AsyncSession = Depends(get_async_session)):
    result = await ItemsService(db_session=session).list()
    return paginate(result)


@router.get("/items/{id}/", tags=["items"], response_model=ItemSchema)
async def get_item(id: int, session: AsyncSession = Depends(get_async_session)):
    return await ItemsService(db_session=session).get(id)


@router.post("/items/", tags=["items"], response_model=ItemSchemaOut)
async def create_item(item: ItemSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await ItemsService(db_session=session).create(item)


@router.put("/items/{id}/", tags=["items"], response_model=ItemSchemaOut)
async def update_item(id: int, item: ItemSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await ItemsService(db_session=session).update(id, item)


@router.patch("/items/{id}/", tags=["items"], response_model=ItemSchemaOut)
async def partial_update_item(id: int, item: ItemSchemaIn, session: AsyncSession = Depends(get_async_session)):
    item = item.model_dump(exclude_unset=True)
    print(item)
    return await ItemsService(db_session=session).partial_update(id, item)


@router.delete("/items/{id}/", tags=["items"])
async def delete_item(id: int, session: AsyncSession = Depends(get_async_session)):
    return await ItemsService(db_session=session).delete(id)


@router.get("/sales-orders/", tags=["sales-orders"], response_model=LimitOffsetPage[SalesOrderSchema])
async def get_salesorders(session: AsyncSession = Depends(get_async_session)):
    result = await SalesOrdersService(db_session=session).list()
    return paginate(result)


@router.get("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def get_salesorder(id: int, session: AsyncSession = Depends(get_async_session)):
    return await SalesOrdersService(db_session=session).get(id)


@router.post("/sales-orders/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def create_salesorder(salesorder: SalesOrderSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await SalesOrdersService(db_session=session).create(salesorder)


@router.put("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def update_salesorder(id: int, salesorder: SalesOrderSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await SalesOrdersService(db_session=session).update(id, salesorder)


@router.patch("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def partial_update_salesorder(id: int, salesorder: SalesOrderSchemaIn, session: AsyncSession = Depends(get_async_session)):
    salesorder = salesorder.model_dump(exclude_unset=True)
    return await SalesOrdersService(db_session=session).partial_update(id, salesorder)


@router.delete("/sales-orders/{id}/", tags=["sales-orders"])
async def delete_salesorder(id: int, session: AsyncSession = Depends(get_async_session)):
    return await SalesOrdersService(db_session=session).delete(id)


@router.get("/flows/", tags=["flows"], response_model=LimitOffsetPage[FlowSchema])
async def get_flows(session: AsyncSession = Depends(get_async_session)):
    result = await FlowsService(db_session=session).list()
    return paginate(result)


@router.get("/flows/{id}/", tags=["flows"], response_model=FlowSchema)
async def get_flow(id: int, session: AsyncSession = Depends(get_async_session)):
    return await FlowsService(db_session=session).get(id)


@router.post("/flows/", tags=["flows"], response_model=FlowSchemaOut)
async def create_flow(flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await FlowsService(db_session=session).create(flow)


@router.put("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def update_flow(id: int, flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session)):
    return await FlowsService(db_session=session).update(id, flow)


@router.patch("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def partial_update_flow(id: int, flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session)):
    flow = flow.model_dump(exclude_unset=True)
    return await FlowsService(db_session=session).partial_update(id, flow)


@router.delete("/flows/{id}/", tags=["flows"])
async def delete_flow(id: int, session: AsyncSession = Depends(get_async_session)):
    return await FlowsService(db_session=session).delete(id)
