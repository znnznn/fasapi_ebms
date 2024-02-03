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
from origin_db.schemas import ArinvSchema, ArinvRelatedArinvDetSchema, CategorySchema
from origin_db.services import CategoryService
from stages.models import Flow
from stages.services import FlowsService, ItemsService, CapacitiesService

router = APIRouter(prefix="/ebms", tags=["ebms"])


@router.get("/orders", response_model=LimitOffsetPage[ArinvRelatedArinvDetSchema])
async def orders(limit: int = 100, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    time1 = time.time()
    list_of_orders = select(Arinv).offset(offset).limit(limit).order_by(Arinv.recno5)
    result = await session.scalars(list_of_orders)
    print(time.time() - time1)
    return paginate(result.all())


@router.get("/orders/{order_id}", response_model=list[ArinvRelatedArinvDetSchema])
async def order_retrieve(order_id: int, session: AsyncSession = Depends(get_async_session)):
    time1 = time.time()
    # details = aliased(Arinvdet, name="details", flat=True)
    list_of_orders = select(Arinv).where(Arinv.recno5 == order_id).join(Arinvdet).options(selectinload(Arinv.details, Arinvdet.rel_item)
                                                                                          ).order_by()
    result = await session.scalars(list_of_orders)
    print(time.time() - time1)
    return result.all()


@router.get("/categories", response_model=LimitOffsetPage[CategorySchema])
async def get_categories(session: AsyncSession = Depends(get_async_session)):
    origin_db_response = await CategoryService(db_session=session).list()
    flows_data = await FlowsService(db_session=session).group_by_category()
    item_ids = await ItemsService(db_session=session).get_autoid_by_production_date(datetime.date.today())
    paginate(item_ids)
    print("+++++++++++++------+++++++++++++")
    item_ids = item_ids if item_ids else ["-1"]
    capacities = await CapacitiesService(db_session=session).list()
    total_capacity = select(Arinvdet.quan, Arinvdet.heightd, Arinvdet.demd).where(Arinvdet.autoid.in_(item_ids)).group_by(
        Arinvdet.inven, Arinvdet.quan, Arinvdet.heightd, Arinvdet.demd
    )
    total_capacity = await session.scalars(total_capacity)
    total_capacity = total_capacity.all()
    print(total_capacity)
    print("+++++++++++++------+++++++++++++")
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
