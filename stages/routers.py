from typing import List

from fastapi import Depends, APIRouter
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants import Role
from database import get_async_session
from stages.filters import ItemFilter
from stages.services import CapacitiesService, StagesService, FlowsService, CommentsService, ItemsService, SalesOrdersService
from stages.schemas import (
    CapacitySchema, CapacitySchemaIn, StageSchema, StageSchemaIn, CommentSchemaIn, CommentSchema, ItemSchema, ItemSchemaIn,
    SalesOrderSchema, SalesOrderSchemaIn, FlowSchema, FlowSchemaIn, FlowSchemaOut, ItemSchemaOut, FlowPaginatedSchema, SalesPaginatedSchema,
    PaginatedItemSchema, CommentPaginatedSchema, StagePaginatedSchema, CapacityPaginatedSchema, MultiUpdateItemSchema,
    MultiUpdateSalesOrderSchema
)
from users.mixins import IsAuthenticatedAs, active_user_with_permission
from users.models import User
from websockets_connection.managers import connection_manager

router = APIRouter()


@router.post("/capacities/", response_model=CapacitySchema, tags=["capacity"])
async def create_capacity(
        store: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    await connection_manager.broadcast("items")
    return await CapacitiesService(db_session=session).create(store)


@router.get("/capacities/", tags=["capacity"], response_model=CapacityPaginatedSchema)
async def get_capacities(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN)),
):
    result = await CapacitiesService(db_session=session).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def get_capacity(id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    return await CapacitiesService(db_session=session).get(id)


@router.put("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def update_capacity(
        id: int, capacity: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    await connection_manager.broadcast("items")
    return await CapacitiesService(db_session=session).update(id, capacity)


@router.patch("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def partial_update_capacity(
        id: int, capacity: CapacitySchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    capacity = capacity.model_dump(exclude_unset=True)
    await connection_manager.broadcast("items")
    return await CapacitiesService(db_session=session).partial_update(id, capacity)


@router.delete("/capacities/{id}/", tags=["capacity"])
async def delete_capacity(
        id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    await connection_manager.broadcast("items")
    return await CapacitiesService(db_session=session).delete(id)


@router.get("/stages/", tags=["stage"], response_model=StagePaginatedSchema)
async def get_stages(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission)
):
    result = await StagesService(db_session=session).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def get_stage(id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(active_user_with_permission)):
    return await StagesService(db_session=session).get(id)


@router.post("/stages/", tags=["stage"], response_model=StageSchema)
async def create_stage(
        stage: StageSchemaIn, session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await StagesService(db_session=session).create(stage)


@router.put("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def update_stage(
        id: int, stage: StageSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    await connection_manager.broadcast("items")
    return await StagesService(db_session=session).update(id, stage)


@router.patch("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def partial_update_stage(
        id: int, data: StageSchemaIn,
        session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    stage = data.model_dump(exclude_unset=True)
    await connection_manager.broadcast("items")
    return await StagesService(db_session=session).partial_update(id, stage)


@router.delete("/stages/{id}/", tags=["stage"])
async def delete_stage(id: int, session: AsyncSession = Depends(get_async_session), user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    await connection_manager.broadcast("items")
    return await StagesService(db_session=session).delete(id)


@router.get("/comments/", tags=["comments"], response_model=CommentPaginatedSchema)
async def get_comments(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    result = await CommentsService(db_session=session).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def get_comment(
        id: int,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    return await CommentsService(db_session=session).get(id)


@router.post("/comments/", tags=["comments"], response_model=CommentSchema)
async def create_comment(
        comment: CommentSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await CommentsService(db_session=session).create(comment)


@router.put("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def update_comment(
        id: int, comment: CommentSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await CommentsService(db_session=session).update(id, comment)


@router.patch("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def partial_update_comment(
        id: int, comment: CommentSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    comment = comment.model_dump(exclude_unset=True)
    await connection_manager.broadcast("items")
    return await CommentsService(db_session=session).partial_update(id, comment)


@router.delete("/comments/{id}/", tags=["comments"])
async def delete_comment(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await CommentsService(db_session=session).delete(id)


@router.get("/items/", tags=["items"], response_model=PaginatedItemSchema)
async def get_items(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    result = await ItemsService(db_session=session, list_filter=item_filter).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/items/{id}/", tags=["items"], response_model=ItemSchema)
async def get_item(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    return await ItemsService(db_session=session).get(id)


@router.post("/items/", tags=["items"], response_model=ItemSchemaOut)
async def create_item(
        item: ItemSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await ItemsService(db_session=session).create(item)


@router.put("/items/{id}/", tags=["items"], response_model=ItemSchemaOut)
async def update_item(
        id: int, item: ItemSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    if hasattr(item, "flow_id"):
        if not getattr(item, "stage_id", None):
            item.stage_id = None
    await connection_manager.broadcast("items")
    return await ItemsService(db_session=session).update(id, item)


@router.patch("/items/{id}/", tags=["items"], response_model=ItemSchemaOut)
async def partial_update_item(
        id: int, item: ItemSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    if hasattr(item, "flow_id"):
        if not getattr(item, "stage_id", None):
            item.stage_id = None
    item = item.model_dump(exclude_unset=True)
    await connection_manager.broadcast("items")
    return await ItemsService(db_session=session).partial_update(id, item)


@router.delete("/items/{id}/", tags=["items"])
async def delete_item(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await ItemsService(db_session=session).delete(id)


@router.get("/sales-orders/", tags=["sales-orders"], response_model=SalesPaginatedSchema)
async def get_salesorders(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    result = await SalesOrdersService(db_session=session).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def get_salesorder(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    return await SalesOrdersService(db_session=session).get(id)


@router.post("/sales-orders/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def create_salesorder(
        salesorder: SalesOrderSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    await connection_manager.broadcast("orders")
    return await SalesOrdersService(db_session=session).create(salesorder)


@router.put("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def update_salesorder(
        id: int, salesorder: SalesOrderSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    await connection_manager.broadcast("orders")
    return await SalesOrdersService(db_session=session).update(id, salesorder)


@router.patch("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def partial_update_salesorder(
        id: int, salesorder: SalesOrderSchemaIn,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    salesorder = salesorder.model_dump(exclude_unset=True)
    await connection_manager.broadcast("orders")
    return await SalesOrdersService(db_session=session).partial_update(id, salesorder)


@router.delete("/sales-orders/{id}/", tags=["sales-orders"])
async def delete_salesorder(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    await connection_manager.broadcast("orders")
    return await SalesOrdersService(db_session=session).delete(id)


@router.get("/flows/all/", tags=["flows"], response_model=List[FlowSchemaOut])
async def get_all_flows(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission),
):
    result = await FlowsService(db_session=session).list()
    return result


@router.get("/flows/", tags=["flows"], response_model=FlowPaginatedSchema)
async def get_flows(
        limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission)
):
    result = await FlowsService(db_session=session).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/flows/{id}/", tags=["flows"], response_model=FlowSchema)
async def get_flow(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission)
):
    return await FlowsService(db_session=session).get(id)


@router.post("/flows/", tags=["flows"], response_model=FlowSchemaOut)
async def create_flow(
        flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await FlowsService(db_session=session).create(flow)


@router.put("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def update_flow(
        id: int, flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await FlowsService(db_session=session).update(id, flow)


@router.patch("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def partial_update_flow(
        id: int, flow: FlowSchemaIn, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    flow = flow.model_dump(exclude_unset=True)
    return await FlowsService(db_session=session).partial_update(id, flow)


@router.delete("/flows/{id}/", tags=["flows"])
async def delete_flow(
        id: int, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    await connection_manager.broadcast("items")
    return await FlowsService(db_session=session).delete(id)


@router.post("/multiupdate/items/", tags=["multiupdate"], response_model=MultiUpdateItemSchema)
async def multiupdate_items(
        items: MultiUpdateItemSchema, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    await connection_manager.broadcast("items")
    return await ItemsService(db_session=session).multiupdate(items)


@router.post("/multiupdate/orders/", tags=["multiupdate"], response_model=MultiUpdateSalesOrderSchema)
async def multiupdate_salesorders(
        salesorders: MultiUpdateSalesOrderSchema, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    await connection_manager.broadcast("orders")
    return await SalesOrdersService(db_session=session).multiupdate(salesorders)


@router.get("/healthcheck/", tags=["healthcheck"])
async def healthcheck(session: AsyncSession = Depends(get_async_session)):
    return {"status": "ok"}
