from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from origin_db.filters import CategoryFilter, OriginItemFilter
from origin_db.schemas import ArinvRelatedArinvDetSchema, ArinPaginateSchema, ArinvDetPaginateSchema, CategoryPaginateSchema, CategorySchema
from origin_db.services import CategoryService, OriginOrderService, OriginItemService, InventryService
from stages.filters import ItemFilter
from stages.services import FlowsService, ItemsService, CapacitiesService, SalesOrdersService

router = APIRouter(prefix="/ebms", tags=["ebms"])


@router.get("/orders/", response_model=ArinPaginateSchema)
async def orders(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    result = await OriginOrderService(db_session=session).list(limit=limit, offset=offset)
    autoids = [i.autoid for i in result["results"]]
    items_dates = await ItemsService(db_session=session).group_by_order_annotated_statistics(autoids=autoids)
    sales_order = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    items_dates = {i.order: i for i in items_dates}
    items = await ItemsService(db_session=session).get_related_items_by_order(autoids=autoids)
    items = {i.origin_item: i for i in items}
    sales_order_data = {i.order: i for i in sales_order}
    for i in result["results"]:
        if order := items_dates.get(i.autoid):
            i.start_date = order.min_date
            i.end_date = order.max_date
            i.completed = order.completed
        if order := sales_order_data.get(i.autoid):
            i.sales_order = order
        for detail in i.details:
            if item := items.get(detail.autoid):
                detail.completed = True if item.production_date and item.stage.name == 'Done' else False
                detail.item = item
    return result


@router.get("/orders/{order_id}/", response_model=ArinvRelatedArinvDetSchema)
async def order_retrieve(autoid: str, session: AsyncSession = Depends(get_async_session)):
    result = await OriginOrderService(db_session=session).get(autoid=autoid)
    autoids = [result.autoid]
    items = await ItemsService(db_session=session).group_by_order_annotated_statistics(autoids=autoids)
    sales_order = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    related_items = await ItemsService(db_session=session).get_related_items_by_order(autoids=autoids)
    items_statistic_data = {i.order: i for i in items}
    items_data = {i.origin_item: i for i in related_items}
    sales_order_data = {i.order: i for i in sales_order}
    if item := items_statistic_data.get(result.autoid):
        result.start_date = item.min_date
        result.end_date = item.max_date
        result.completed = item.completed
    if order := sales_order_data.get(result.autoid):
        result.sales_order = order
    for detail in result.details:
        if item := items_data.get(detail.autoid):
            detail.completed = True if item.production_date and item.stage.name == 'Done' else False
            detail.item = item
    return result


@router.get("/categories/", response_model=CategoryPaginateSchema)
async def get_categories(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        category_filter: CategoryFilter = FilterDepends(CategoryFilter),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
):
    result = await CategoryService(db_session=session, list_filter=category_filter).paginated_list(limit=limit, offset=offset)
    flows_data = await FlowsService(db_session=session).group_by_category()
    item_ids = await ItemsService(db_session=session).get_autoid_by_production_date(production_date=item_filter.production_date)
    item_ids = item_ids if item_ids else ["-1"]
    capacities = await CapacitiesService(db_session=session).list()
    total_capacity = await InventryService(db_session=session).count_capacity(autoids=item_ids)
    total_capacity = {i.prod_type: i.total_capacity for i in total_capacity}
    capacities_data = {c.category_autoid: c for c in capacities}
    for category in result["results"]:
        capacity = capacities_data.get(category.autoid)
        category.flow_count = flows_data.get(category.autoid)
        category.capacity = capacity.per_day if capacity else None
        category.capacity_id = capacity.id if capacity else None
        if category_total_capacity := total_capacity.get(category.prod_type):
            category.total_capacity = category_total_capacity
    return result


@router.get("/categories/all/", response_model=list[CategorySchema])
async def get_categories_all(
        session: AsyncSession = Depends(get_async_session),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        category_filter: CategoryFilter = FilterDepends(CategoryFilter),
):
    result = await CategoryService(db_session=session, list_filter=category_filter).list()
    flows_data = await FlowsService(db_session=session).group_by_category()
    item_ids = await ItemsService(db_session=session).get_autoid_by_production_date(production_date=item_filter.production_date)
    item_ids = item_ids if item_ids else ["-1"]
    capacities = await CapacitiesService(db_session=session).list()
    total_capacity = await InventryService(db_session=session).count_capacity(autoids=item_ids)
    total_capacity = {i.prod_type: i.total_capacity for i in total_capacity}
    capacities_data = {c.category_autoid: c for c in capacities}
    for category in result:
        capacity = capacities_data.get(category.autoid)
        category.flow_count = flows_data.get(category.autoid)
        category.capacity = capacity.per_day if capacity else None
        category.capacity_id = capacity.id if capacity else None
        if category_total_capacity := total_capacity.get(category.prod_type):
            category.total_capacity = category_total_capacity
    return result


@router.get("/items/", response_model=ArinvDetPaginateSchema)
async def get_items(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        origin_item_filter: OriginItemFilter = FilterDepends(OriginItemFilter),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
):
    filtering_items = await ItemsService(db_session=session, list_filter=item_filter).get_filtering_origin_items_autoids()
    print(filtering_items)
    if filtering_items:
        filtering_fields = origin_item_filter.model_dump(exclude_unset=True, exclude_none=True)
        if item_filter.is_exclude:
            filtering_fields["autoid__not_in"] = filtering_items
        else:
            filtering_fields["autoid__in"] = filtering_items
        origin_item_filter = OriginItemFilter(**filtering_fields)
    result = await OriginItemService(db_session=session, list_filter=origin_item_filter).list(limit=limit, offset=offset)
    autoids = [i.autoid for i in result["results"]]
    items_statistic = await ItemsService(db_session=session).group_by_item_statistics(autoids=autoids)
    related_items = await ItemsService(db_session=session).get_related_items_by_origin_items(autoids=autoids)
    items_statistic_data = {i.origin_item: i for i in items_statistic}
    items_data = {i.origin_item: i for i in related_items}
    for origin_item in result["results"]:
        if item := items_statistic_data.get(origin_item.autoid):
            origin_item.completed = item.completed
        if item := items_data.get(origin_item.autoid):
            origin_item.item = item
    return result
