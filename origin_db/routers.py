import datetime
import time
from pprint import pprint
from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage, paginate
from sqlalchemy import select, func, label, cast, Integer, String, text
from sqlalchemy.orm import joinedload, selectinload, subqueryload, with_loader_criteria, aliased, join
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from database import get_async_session
from origin_db.models import Arinv, Arinvdet, Inprodtype
# from origin_db.models import create_cache
from origin_db.schemas import ArinvSchema, ArinvRelatedArinvDetSchema, CategorySchema, ArinPaginateSchema, ArinvDetPaginateSchema
from origin_db.services import CategoryService, OriginOrderService, OriginItemService
from stages.models import Flow, SalesOrder, Item
from stages.services import FlowsService, ItemsService, CapacitiesService, SalesOrdersService

router = APIRouter(prefix="/ebms", tags=["ebms"])


@router.get("/orders/", response_model=ArinPaginateSchema)
async def orders(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    result = await OriginOrderService(db_session=session).list(limit=limit, offset=offset)
    autoids = [i.autoid for i in result["results"]]
    items_dates = await ItemsService(db_session=session).group_by_order_annotated_statistics(autoids=autoids)
    sales_order = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    items_dates = {i.order: i for i in items_dates}
    items = await ItemsService(db_session=session).get_related_items(autoids=autoids)
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
                detail.item = item
    return result


@router.get("/orders/{order_id}/", response_model=ArinvRelatedArinvDetSchema)
async def order_retrieve(autoid: str, session: AsyncSession = Depends(get_async_session)):
    result = await OriginOrderService(db_session=session).get(autoid=autoid)
    autoids = [result.autoid]
    items = await ItemsService(db_session=session).get_min_max_production_date(autoids=autoids)
    sales_order = await SalesOrdersService(db_session=session).list_by_orders(autoids=autoids)
    items_data = {i.order: i for i in items}
    sales_order_data = {i.order: i for i in sales_order}
    if item := items_data.get(result.autoid):
        result.start_date = item.min_date
        result.end_date = item.max_date
    if order := sales_order_data.get(result.autoid):
        result.sales_order = order
    return result


@router.get("/categories/", response_model=LimitOffsetPage[CategorySchema])
async def get_categories(session: AsyncSession = Depends(get_async_session)):
    origin_db_response = await CategoryService(db_session=session).list()
    flows_data = await FlowsService(db_session=session).group_by_category()
    item_ids = await ItemsService(db_session=session).get_autoid_by_production_date(datetime.date.today())
    item_ids = item_ids if item_ids else ["-1"]
    capacities = await CapacitiesService(db_session=session).list()
    total_capacity = select(Arinvdet.quan, Arinvdet.heightd, Arinvdet.demd).where(Arinvdet.autoid.in_(item_ids)).group_by(
        Arinvdet.inven, Arinvdet.quan, Arinvdet.heightd, Arinvdet.demd
    )
    total_capacity = await session.scalars(total_capacity)
    total_capacity = total_capacity.all()
    print(total_capacity)
    capacities_data = {c.category_autoid: c for c in capacities}
    result = paginate(origin_db_response)
    print(result.items)
    for category in result.items:
        capacity = capacities_data.get(category.id)
        category.flow_count = flows_data.get(category.id)
        category.capacity = capacity.per_day if capacity else None
        category.capacity_id = capacity.id if capacity else None
        # category.total_capacity = capacity.total if capacity else None
    return result


@router.get("/items/", response_model=ArinvDetPaginateSchema)
async def get_items(limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    result = await OriginItemService(db_session=session).list(limit=limit, offset=offset)
    return result
