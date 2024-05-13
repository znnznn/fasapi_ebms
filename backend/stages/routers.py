from typing import List

from fastapi import Depends, APIRouter, BackgroundTasks
from fastapi_filter import FilterDepends

from common.constants import Role
from origin_db.services import CategoryService
from stages.filters import ItemFilter, StageFilter, FlowFilter, SalesOrderFilter
from stages.services import CapacitiesService, StagesService, FlowsService, CommentsService, ItemsService, SalesOrdersService
from stages.schemas import (
    CapacitySchema, CapacitySchemaIn, StageSchema, StageSchemaIn, CommentSchemaIn, CommentSchema, ItemSchema, ItemSchemaIn,
    SalesOrderSchema, SalesOrderSchemaIn, FlowSchema, FlowSchemaIn, FlowSchemaOut, ItemSchemaOut, FlowPaginatedSchema, SalesPaginatedSchema,
    PaginatedItemSchema, CommentPaginatedSchema, StagePaginatedSchema, CapacityPaginatedSchema, MultiUpdateItemSchema,
    MultiUpdateSalesOrderSchema
)
from stages.utils import send_data_to_ws, send_calendars_data_to_ws
from users.mixins import IsAuthenticatedAs, active_user_with_permission
from users.models import User

router = APIRouter()


@router.post("/capacities/", response_model=CapacitySchema, tags=["capacity"])
async def create_capacity(store: CapacitySchemaIn, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    result = await CapacitiesService().create(store)
    return result


@router.get("/capacities/", tags=["capacity"], response_model=CapacityPaginatedSchema)
async def get_capacities(
        limit: int = 10, offset: int = 0,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN)),
):
    result = await CapacitiesService().paginated_list(limit=limit, offset=offset)
    return result


@router.get("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def get_capacity(id: int, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    result = await CapacitiesService().get(id)
    return result


@router.put("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def update_capacity(
        id: int, capacity: CapacitySchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    result = await CapacitiesService().update(id, capacity)
    return result


@router.patch("/capacities/{id}/", tags=["capacity"], response_model=CapacitySchema)
async def partial_update_capacity(
        id: int, capacity: CapacitySchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    capacity = capacity.model_dump(exclude_unset=True)
    result = await CapacitiesService().partial_update(id, capacity)
    return result


@router.delete("/capacities/{id}/", tags=["capacity"])
async def delete_capacity(
        id: int, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    result = await CapacitiesService().delete(id)
    return result


@router.get("/stages/", tags=["stage"], response_model=StagePaginatedSchema)
async def get_stages(
        limit: int = 10, offset: int = 0,
        user: User = Depends(active_user_with_permission),
        stage_filter: StageFilter = FilterDepends(StageFilter),
):
    result = await StagesService(list_filter=stage_filter).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def get_stage(id: int, user: User = Depends(active_user_with_permission)):
    return await StagesService().get(id)


@router.post("/stages/", tags=["stage"], response_model=StageSchema)
async def create_stage(
        stage: StageSchemaIn, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await StagesService().create(stage)


@router.put("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def update_stage(id: int, stage: StageSchemaIn, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    return await StagesService().update(id, stage)


@router.patch("/stages/{id}/", tags=["stage"], response_model=StageSchema)
async def partial_update_stage(id: int, data: StageSchemaIn, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    stage = data.model_dump(exclude_unset=True)
    return await StagesService().partial_update(id, stage)


@router.delete("/stages/{id}/", tags=["stage"])
async def delete_stage(id: int, user: User = Depends(IsAuthenticatedAs(Role.ADMIN))):
    return await StagesService().delete(id)


@router.get("/comments/", tags=["comments"], response_model=CommentPaginatedSchema)
async def get_comments(
        limit: int = 10, offset: int = 0,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    result = await CommentsService().paginated_list(limit=limit, offset=offset)
    return result


@router.get("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def get_comment(id: int, user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))):
    return await CommentsService().get(id)


@router.post("/comments/", tags=["comments"], response_model=CommentSchema)
async def create_comment(
        comment: CommentSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await CommentsService().create(comment)
    item = await ItemsService().get(instance.item_id)
    background_tasks.add_task(send_data_to_ws, autoid=item.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=item.order, subscribe="orders")
    return instance


@router.put("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def update_comment(
        id: int, comment: CommentSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await CommentsService().update(id, comment)
    item = await ItemsService().get(instance.item_id)
    background_tasks.add_task(send_data_to_ws, autoid=item.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=item.order, subscribe="orders")
    return instance


@router.patch("/comments/{id}/", tags=["comments"], response_model=CommentSchema)
async def partial_update_comment(
        id: int, comment: CommentSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    comment = comment.model_dump(exclude_unset=True)
    instance = await CommentsService().partial_update(id, comment)
    item = await ItemsService().get(instance.item_id)
    background_tasks.add_task(send_data_to_ws, autoid=item.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=item.order, subscribe="orders")
    return instance


@router.delete("/comments/{id}/", tags=["comments"])
async def delete_comment(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await CommentsService().get(id)
    result = await CommentsService().delete(id)
    item = await ItemsService().get(instance.item_id)
    background_tasks.add_task(send_data_to_ws, autoid=item.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=item.order, subscribe="orders")
    return result


@router.get("/items/", tags=["items"], response_model=PaginatedItemSchema)
async def get_items(
        limit: int = 10, offset: int = 0,
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    result = await ItemsService(list_filter=item_filter).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/items/{id}/", tags=["items"], response_model=ItemSchema)
async def get_item(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER))
):
    return await ItemsService().get(id)


@router.post("/items/", tags=["items"], response_model=ItemSchemaOut)
async def create_item(
        item: ItemSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await ItemsService().create(item)
    background_tasks.add_task(send_data_to_ws, autoid=instance.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    if item.production_date:
        background_tasks.add_task(
            send_calendars_data_to_ws, year=item.production_date.year, month=item.production_date.month
        )
    return instance


@router.put("/items/{id}/", tags=["items"], response_model=ItemSchema)
async def update_item(
        id: int, item: ItemSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await ItemsService().update(id, item)
    instance = await ItemsService().get(instance.id)
    background_tasks.add_task(send_data_to_ws, autoid=instance.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    if item.production_date:
        background_tasks.add_task(
            send_calendars_data_to_ws, year=item.production_date.year, month=item.production_date.month, item_autoid=instance.origin_item
        )
    return instance


@router.patch("/items/{id}/", tags=["items"], response_model=ItemSchema)
async def partial_update_item(
        id: int, item: ItemSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    item_data = item.model_dump(exclude_unset=True)
    instance = await ItemsService().partial_update(id, item_data)
    instance = await ItemsService().get(instance.id)
    background_tasks.add_task(send_data_to_ws, autoid=instance.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    if item.production_date:
        background_tasks.add_task(
            send_calendars_data_to_ws, year=item.production_date.year, month=item.production_date.month, item_autoid=instance.origin_item
        )
    return instance


@router.delete("/items/{id}/", tags=["items"])
async def delete_item(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await ItemsService().get(id)
    background_tasks.add_task(send_data_to_ws, autoid=instance.origin_item, subscribe="items")
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    if instance.production_date:
        background_tasks.add_task(
            send_calendars_data_to_ws, year=instance.production_date.year, month=instance.production_date.month,
            item_autoid=instance.origin_item,
        )
    return await ItemsService().delete(id)


@router.get("/sales-orders/", tags=["sales-orders"], response_model=SalesPaginatedSchema)
async def get_salesorders(
        limit: int = 10, offset: int = 0,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        salesorder_filter: SalesOrderFilter = FilterDepends(SalesOrderFilter)
):
    result = await SalesOrdersService().paginated_list(limit=limit, offset=offset)
    return result


@router.get("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def get_salesorder(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER))
):
    return await SalesOrdersService().get(id)


@router.post("/sales-orders/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def create_salesorder(
        salesorder: SalesOrderSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await SalesOrdersService().create(salesorder)
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    return instance


@router.put("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def update_salesorder(
        id: int, salesorder: SalesOrderSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await SalesOrdersService().update(id, salesorder)
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    return instance


@router.patch("/sales-orders/{id}/", tags=["sales-orders"], response_model=SalesOrderSchema)
async def partial_update_salesorder(
        id: int, salesorder: SalesOrderSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    salesorder = salesorder.model_dump(exclude_unset=True)
    instance = await SalesOrdersService().partial_update(id, salesorder)
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    return instance


@router.delete("/sales-orders/{id}/", tags=["sales-orders"])
async def delete_salesorder(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    instance = await SalesOrdersService().get(id)
    background_tasks.add_task(send_data_to_ws, autoid=instance.order, subscribe="orders")
    return await SalesOrdersService().delete(id)


@router.get("/flows/all/", tags=["flows"], response_model=List[FlowSchemaOut])
async def get_all_flows(
        user: User = Depends(active_user_with_permission),
        flow_filter: FlowFilter = FilterDepends(FlowFilter),
):
    if flow_filter.category__prod_type:
        category = await CategoryService().get_category_autoid_by_name(flow_filter.category__prod_type)
        flow_filter.category__prod_type = category.autoid or ''
    result = await FlowsService(list_filter=flow_filter).list()
    return result


@router.get("/flows/", tags=["flows"], response_model=FlowPaginatedSchema)
async def get_flows(
        limit: int = 10, offset: int = 0,
        user: User = Depends(active_user_with_permission),
        flow_filter: FlowFilter = FilterDepends(FlowFilter),
):
    if flow_filter.category__prod_type:
        category = await CategoryService().get_category_autoid_by_name(flow_filter.category__prod_type)
        flow_filter.category__prod_type = category.autoid or ''
    result = await FlowsService(list_filter=flow_filter).paginated_list(limit=limit, offset=offset)
    return result


@router.get("/flows/{id}/", tags=["flows"], response_model=FlowSchema)
async def get_flow(
        id: int,
        user: User = Depends(active_user_with_permission)
):
    return await FlowsService().get(id)


@router.post("/flows/", tags=["flows"], response_model=FlowSchemaOut)
async def create_flow(
        flow: FlowSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await FlowsService().create(flow)


@router.put("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def update_flow(
        id: int, flow: FlowSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await FlowsService().update(id, flow)


@router.patch("/flows/{id}/", tags=["flows"], response_model=FlowSchemaOut)
async def partial_update_flow(
        id: int, flow: FlowSchemaIn,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    flow = flow.model_dump(exclude_unset=True)
    return await FlowsService().partial_update(id, flow)


@router.delete("/flows/{id}/", tags=["flows"])
async def delete_flow(
        id: int,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN))
):
    return await FlowsService().delete(id)


@router.post("/multiupdate/items/", tags=["multiupdate"], response_model=MultiUpdateItemSchema)
async def multiupdate_items(
        items: MultiUpdateItemSchema,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    response = await ItemsService().multiupdate(items)
    orders_autoids = await ItemsService().get_orders_autoids_by_origin_items(items.origin_items)
    background_tasks.add_task(send_data_to_ws, subscribe="orders", list_autoids=orders_autoids)
    background_tasks.add_task(send_data_to_ws, subscribe="items", list_autoids=items.origin_items)
    return response


@router.post("/multiupdate/orders/", tags=["multiupdate"], response_model=MultiUpdateSalesOrderSchema)
async def multiupdate_salesorders(
        salesorders: MultiUpdateSalesOrderSchema,
        user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.MANAGER)),
        background_tasks: BackgroundTasks = BackgroundTasks()
):
    response = await SalesOrdersService().multiupdate(salesorders)
    background_tasks.add_task(send_data_to_ws, subscribe="orders", list_autoids=salesorders.origin_orders)
    return response


@router.get("/healthcheck/", tags=["healthcheck"])
async def healthcheck():
    return {"status": "ok"}
