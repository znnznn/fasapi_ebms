import time
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException
from fastapi_filter import FilterDepends
from sqlalchemy import case
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from common.utils import DateValidator
from database import get_async_session
from ebms_api.client import ArinvClient
from origin_db.filters import CategoryFilter, OriginItemFilter, OrderFilter
from origin_db.models import Arinvdet, Arinv
from origin_db.schemas import (
    ArinvRelatedArinvDetSchema, ArinPaginateSchema, ArinvDetPaginateSchema, CategoryPaginateSchema,
    CategorySchema, ChangeShipDateSchema
)
from origin_db.services import CategoryService, OriginOrderService, OriginItemService, InventryService
from stages.filters import ItemFilter, SalesOrderFilter
from stages.services import FlowsService, ItemsService, CapacitiesService, SalesOrdersService
from users.mixins import active_user_with_permission
from users.models import User

router = APIRouter(prefix="/ebms", tags=["ebms"])


@router.get("/orders/", response_model=ArinPaginateSchema)
async def orders(
        limit: int = 10, offset: int = 0,
        ordering: str = None,
        session: AsyncSession = Depends(get_async_session),
        origin_order_filter: OrderFilter = FilterDepends(OrderFilter),
        sales_order_filter: SalesOrderFilter = FilterDepends(SalesOrderFilter),
        user: User = Depends(active_user_with_permission),

):
    print('orders')
    time_start = time.time()
    if ordering:
        sales_order_filter.order_by = sales_order_filter.remove_invalid_fields(ordering)
        origin_order_filter.order_by = origin_order_filter.remove_invalid_fields(ordering)
    filtering_sales_orders = await SalesOrdersService(
        db_session=session, list_filter=sales_order_filter
    ).get_filtering_origin_orders_autoids()
    extra_ordering = None
    if filtering_sales_orders:
        if sales_order_filter.is_exclude:
            origin_order_filter.autoid__not_in = filtering_sales_orders
        else:
            origin_order_filter.autoid__in = filtering_sales_orders

    if not sales_order_filter.is_filtering_values and sales_order_filter.order_by:
        filtering_sales_orders = await SalesOrdersService(
            db_session=session, list_filter=sales_order_filter
        ).get_filtering_origin_orders_autoids(do_ordering=True)
    if sales_order_filter.order_by:
        ordering_filds = ''.join(sales_order_filter.order_by)
        default_position = -1
        if ordering_filds.startswith('-'):
            default_position = len(filtering_sales_orders) + 2
        data_for_ordering = {v: i for i, v in enumerate(filtering_sales_orders, 1)}
        extra_ordering = case(data_for_ordering, value=Arinv.autoid, else_=default_position)
    result = await OriginOrderService(
        db_session=session, list_filter=origin_order_filter
    ).list(limit=limit, offset=offset, extra_ordering=extra_ordering)
    print('connected to ebms', time.time() - time_start)
    autoids = [i.autoid for i in result["results"]]
    items_dates = await ItemsService(db_session=session).group_by_order_annotated_statistics(autoids=autoids)
    sales_orders = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    items_dates = {i.order: i for i in items_dates}
    items = await ItemsService(db_session=session).get_related_items_by_order(autoids=autoids)
    items = {i.origin_item: i for i in items}
    sales_order_data = {i.order: i for i in sales_orders}
    for i in result["results"]:
        completed = []
        if order := items_dates.get(i.autoid):
            i.start_date = order.min_date
            i.end_date = order.max_date
            i.completed = order.completed
        if order := sales_order_data.get(i.autoid):
            i.sales_order = order
        for detail in i.details:
            if item := items.get(detail.autoid):
                detail.completed = True if item.production_date and item.stage and item.stage.name == 'Done' else False
                detail.item = item
                completed.append(detail.completed)
            else:
                completed.append(False)
        i.completed = all(completed)
    origin_order_filter.Constants.do_ordering = None
    origin_order_filter.Constants.exclude = None
    origin_order_filter.Constants.joins = set()
    origin_order_filter.Constants.only_exclude = True
    sales_order_filter.Constants.do_ordering = None
    sales_order_filter.Constants.exclude = None
    sales_order_filter.Constants.joins = set()
    sales_order_filter.Constants.only_exclude = True
    print(time.time() - time_start)
    return result


@router.get("/orders/{autoid}/", response_model=ArinvRelatedArinvDetSchema)
async def order_retrieve(
        autoid: str, session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission)
):
    result = await OriginOrderService(db_session=session).get(autoid=autoid)
    autoids = [result.autoid]
    items = await ItemsService(db_session=session).group_by_order_annotated_statistics(autoids=autoids)
    sales_order = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    related_items = await ItemsService(db_session=session).get_related_items_by_order(autoids=autoids)
    items_statistic_data = {i.order: i for i in items}
    items_data = {i.origin_item: i for i in related_items}
    sales_order_data = {i.order: i for i in sales_order}
    completed = []
    if item := items_statistic_data.get(result.autoid):
        result.start_date = item.min_date
        result.end_date = item.max_date
        result.completed = item.completed
    if order := sales_order_data.get(result.autoid):
        result.sales_order = order
    for detail in result.details:
        if item := items_data.get(detail.autoid):
            detail.completed = True if item.stage and item.production_date and item.stage.name == 'Done' else False
            detail.item = item
            completed.append(detail.completed)
        else:
            completed.append(False)
    result.completed = all(completed)
    return result


@router.get("/categories/", response_model=CategoryPaginateSchema)
async def get_categories(
        limit: int = 10, offset: int = 0,
        session: AsyncSession = Depends(get_async_session),
        category_filter: CategoryFilter = FilterDepends(CategoryFilter),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        user: User = Depends(active_user_with_permission),
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
    category_filter.Constants.do_ordering = None
    category_filter.Constants.exclude = None
    category_filter.Constants.joins = set()
    category_filter.Constants.only_exclude = True
    item_filter.Constants.do_ordering = None
    item_filter.Constants.exclude = None
    item_filter.Constants.joins = set()
    item_filter.Constants.only_exclude = True
    return result


@router.get("/categories/all/", response_model=list[CategorySchema])
async def get_categories_all(
        session: AsyncSession = Depends(get_async_session),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        category_filter: CategoryFilter = FilterDepends(CategoryFilter),
        user: User = Depends(active_user_with_permission),
):
    result = await CategoryService(db_session=session, list_filter=category_filter).list()
    flows_data = await FlowsService(db_session=session).group_by_category()
    item_ids = await ItemsService(db_session=session).get_autoid_by_production_date(
        production_date=item_filter.production_date
    )
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
    category_filter.Constants.do_ordering = None
    category_filter.Constants.exclude = None
    category_filter.Constants.joins = set()
    category_filter.Constants.only_exclude = True
    item_filter.Constants.do_ordering = None
    item_filter.Constants.exclude = None
    item_filter.Constants.joins = set()
    item_filter.Constants.only_exclude = True
    return result


@router.get("/items/", response_model=ArinvDetPaginateSchema)
async def get_items(
        limit: int = 10, offset: int = 0, ordering: str = None,
        session: AsyncSession = Depends(get_async_session),
        origin_item_filter: OriginItemFilter = FilterDepends(OriginItemFilter),
        item_filter: ItemFilter = FilterDepends(ItemFilter),
        user: User = Depends(active_user_with_permission),
):
    print('items')
    time_start = time.time()
    if ordering:
        item_filter.order_by = item_filter.remove_invalid_fields(ordering)
        origin_item_filter.order_by = origin_item_filter.remove_invalid_fields(ordering)
    filtering_items = await ItemsService(db_session=session, list_filter=item_filter).get_filtering_origin_items_autoids()
    print(filtering_items)
    extra_ordering = None
    if filtering_items:
        if item_filter.is_exclude:
            origin_item_filter.autoid__not_in = filtering_items
        else:
            origin_item_filter.autoid__in = filtering_items
    if not item_filter.is_filtering_values and item_filter.order_by:
        filtering_items = await ItemsService(db_session=session, list_filter=item_filter).get_filtering_origin_items_autoids(do_ordering=True)
    if item_filter.order_by:
        ordering_fields = ''.join(item_filter.order_by)
        default_position = -1
        if ordering_fields.startswith('-'):
            default_position = len(filtering_items) + 2
        data_for_ordering = {v: i for i, v in enumerate(filtering_items, 1)}
        extra_ordering = case(data_for_ordering, value=Arinvdet.autoid, else_=default_position)
    result = await OriginItemService(
        db_session=session, list_filter=origin_item_filter
    ).list(
        limit=limit, offset=offset, extra_ordering=extra_ordering
    )
    print('connected to ebms', time.time() - time_start)
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
    origin_item_filter.Constants.do_ordering = None
    origin_item_filter.Constants.exclude = None
    origin_item_filter.Constants.joins = set()
    origin_item_filter.Constants.only_exclude = True
    item_filter.Constants.do_ordering = None
    item_filter.Constants.exclude = None
    item_filter.Constants.only_exclude = True
    item_filter.Constants.joins = set()
    print(time.time() - time_start)
    return result


@router.get("/calendar/{year}/{month}/", name="capacities_by_month", response_model=dict[str, dict])
async def get_capacities_calendar(
        year: int, month: int,
        session: AsyncSession = Depends(get_async_session), category_filter: CategoryFilter = FilterDepends(CategoryFilter),
        user: User = Depends(active_user_with_permission),
):
    DateValidator.validate_year(year)
    DateValidator.validate_month(month)
    list_of_days = DateValidator.get_month_days(year=year, month=month)
    context = {}
    for day in list_of_days:
        context[day] = {}
    categories = await CategoryService(db_session=session, list_filter=category_filter).list()
    categories_data = {c.autoid: c.prod_type for c in categories}
    item_objs = await ItemsService(db_session=session).get_autoids_and_production_date_by_month(year=year, month=month)
    items_data = {i.origin_item: i.production_date for i in item_objs}
    capacities = await CapacitiesService(db_session=session).list()
    total_capacity = await InventryService(db_session=session).count_capacity_by_days(items_data=items_data) if items_data else []
    for capacity in total_capacity:
        context[capacity.production_date] = {
            capacity.prod_type: {"capacity": float(capacity.total_capacity), "count_orders": capacity.count_orders}
        }
    context['capacity_data'] = {categories_data.get(capacity.category_autoid): capacity.per_day for capacity in capacities}
    return JSONResponse(content=context)


@router.patch("/items/{autoid}/", response_model=dict)
async def partial_update_item(
        autoid: str, origin_item: ChangeShipDateSchema,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(active_user_with_permission),
):
    instance = await OriginOrderService(db_session=session).get_object_or_404(autoid=autoid)
    ebms_api_client = ArinvClient()
    response = ebms_api_client.patch(ebms_api_client.retrieve_url(instance.autoid), {"SHIP_DATE": origin_item.ship_date})
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return {"message": response.json()}


@router.get("/orderss-api/{autoid}/", response_model=dict)
async def get_item_by_ebms_api (autoid: str, session: AsyncSession = Depends(get_async_session)):
    ebms_api_client = ArinvClient()
    response = ebms_api_client.get(ebms_api_client.retrieve_url(autoid))
    return {"data": response.json()}
