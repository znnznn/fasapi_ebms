import time
from pprint import pprint
from typing import List

from fastapi import APIRouter, Depends
from fastapi_pagination import LimitOffsetPage
from sqlalchemy import select, func, label, cast, Integer, String, text
from sqlalchemy.orm import joinedload, selectinload, subqueryload, with_loader_criteria, aliased
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from database import get_async_session
from origin_db.models import Arinv, Arinvdet, Inprodtype
# from origin_db.models import create_cache
from origin_db.schemas import ArinvSchema, ArinvRelatedArinvDetSchema, CategorySchema

router = APIRouter(prefix="/ebms", tags=["ebms"])


@router.get("/orders", response_model=list[ArinvSchema])
async def orders(limit: int = 100, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    time1 = time.time()
    list_of_orders = select(Arinv).offset(offset).limit(limit).order_by(Arinv.recno5)
    result = await session.scalars(list_of_orders)
    print(time.time() - time1)
    return result.all()


@router.get("/orders/{order_id}", response_model=list[ArinvRelatedArinvDetSchema])
async def order_retrieve(order_id: int, session: AsyncSession = Depends(get_async_session)):
    time1 = time.time()
    # details = aliased(Arinvdet, name="details", flat=True)
    list_of_orders = select(Arinv).where(Arinv.recno5 == order_id).join(Arinvdet).options(selectinload(Arinv.details, Arinvdet.rel_item)
                                                                                          ).order_by()
    result = await session.scalars(list_of_orders)
    print(time.time() - time1)
    return result.all()


@router.get("/categories", response_model=LimitOffsetPage [CategorySchema])
async def get_categories(limit: int = 100, offset: int = 0, session: AsyncSession = Depends(get_async_session)):
    time1 = time.time()
    # count_flow = aliased(Flow, name="count_flow")
    # count_flow = func.count(Inprodtype.flows).label("flow_count")
    # count = select(Flow.category_id, func.count(Flow.category_id).label("flow_count")).group_by(Flow.category_id)
    # count = select(Inprodtype, label("flow_count", func.count(Flow.category_id))).group_by(Inprodtype).select_from(
    #     Inprodtype, Flow
    # )
    # # count = select(Flow.category_id, func.count(Flow.category_id).label("flow_count")).group_by(Flow.category_id).subquery()
    # # count = select(func.count(Flow.category_id).label("flow_count")).group_by(Inprodtype).subquery()
    # result = await session.scalars(count)
    # for i in result:
    #     print(i)
    #     print(i.__dict__)
    # subq = (
    #     select(
            # Inprodtype.autoid.label("autoid"),# Inprodtype.prod_type.label("prod_type"), Inprodtype.inprodtype_guid.label("guid"),
            #Inprodtype.ar_aid.label("ar_aid"), Inprodtype.inprodtype_guid.label("inprodtype_guid"),
            # cast(func.count(Flow.category_id), Integer).label("flow_count"),
            # func.sum(Capacity.per_day).cast(Integer).label("capacity")

            # count
            # subqueryload(select(func.count(Flow.category_id).label("flow_count")).group_by(Inprodtype.recno5)),
        # )
        # .select_from(Inprodtype, Flow)
        # .group_by(
        #     Inprodtype.autoid, #Inprodtype.prod_type, Inprodtype.inprodtype_guid, Inprodtype.ar_aid, Inprodtype.inprodtype_guid, #Capacity.per_day
        # ).subquery()
    # )
    print("//////////////////")
    # print(subq)
    # cte = (select(
    #     subq.c.flow_count, subq.c.autoid,
    #     #subq.c.guid, subq.c.prod_type, subq.c.ar_aid,
    #     #subq.c.inprodtype_guid,
    # ).cte())
    print("//////////////////")
    # print(str(cte))
    # list_of_orders = select(
    #     Inprodtype, count_flow).offset(offset).limit(limit).options(subqueryload(Inprodtype.flows))
    print("++++++++++++++++++++++++++++++++++++++")
    # query = (select(cte)
    # .options(
    #     joinedload(Inprodtype.flows).selectinload(Flow.stages)
    # )
    # )
    query = (
        select(
            Inprodtype,

            # func.count(Flow.category_id).cast(Integer).label("flow_count")
        # ).join(
            # Flow, Inprodtype.autoid == Flow.category_id
        # ).options(
            # selectinload(Inprodtype.flows).selectinload(Flow.stages)
        ).group_by(Inprodtype)
    )
    result = await session.scalars(query)
    response = result.all()
    print(response[0].__dict__)
    print(response[1].__dict__)
    print(response[2].__dict__)
    print(response[3].__dict__)
    print(time.time() - time1)
    return response
