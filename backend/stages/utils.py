from sqlalchemy.ext.asyncio import AsyncSession

from origin_db.schemas import ArinvDetSchema, ArinvRelatedArinvDetSchema, ArinvDetPaginateSchema
from origin_db.services import OriginItemService, OriginOrderService
from stages.services import ItemsService, SalesOrdersService


class GetDataForSending:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def one_origin_item_object(self, autoid: str) -> dict:
        origin_item = await OriginItemService(db_session=self.db_session).get_origin_item_with_item(autoid)
        items_statistic = await ItemsService(db_session=self.db_session).group_by_item_statistics(autoids=[origin_item.autoid])
        related_items = await ItemsService(db_session=self.db_session).get_related_items_by_origin_items(autoids=[origin_item.autoid])
        items_statistic_data = {i.origin_item: i for i in items_statistic}
        items_data = {i.origin_item: i for i in related_items}
        if added_item := items_statistic_data.get(origin_item.autoid):
            origin_item.completed = added_item.completed
        if added_item := items_data.get(origin_item.autoid):
            origin_item.item = added_item
        data = ArinvDetSchema.from_orm(origin_item).model_dump()
        return data

    async def one_origin_order_object(self, autoid: str) -> dict:
        result = await OriginOrderService(db_session=self.db_session).get(autoid=autoid)
        autoids = [result.autoid]
        items = await ItemsService(db_session=self.db_session).group_by_order_annotated_statistics(autoids=autoids)
        sales_order = await SalesOrdersService(db_session=self.db_session).list_by_orders(autoids=autoids)
        related_items = await ItemsService(db_session=self.db_session).get_related_items_by_order(autoids=autoids)
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
        return ArinvRelatedArinvDetSchema.from_orm(result).model_dump()

    async def get_items_by_autoids(self, autoids: list) -> list[dict]:
        origin_items = await OriginItemService(db_session=self.db_session).get_listy_by_autoids(autoids=autoids)
        autoids = [i.autoid for i in origin_items]
        items_statistic = await ItemsService(db_session=self.db_session).group_by_item_statistics(autoids=autoids)
        related_items = await ItemsService(db_session=self.db_session).get_related_items_by_origin_items(autoids=autoids)
        items_statistic_data = {i.origin_item: i for i in items_statistic}
        items_data = {i.origin_item: i for i in related_items}
        for origin_item in origin_items:
            if item := items_statistic_data.get(origin_item.autoid):
                origin_item.completed = item.completed
            if item := items_data.get(origin_item.autoid):
                origin_item.item = item
        return [ArinvDetSchema.from_orm(i).model_dump() for i in origin_items]

    async def get_orders_by_autoids(self, autoids: list) -> list[dict]:
        origin_orders = await OriginOrderService(db_session=self.db_session).get_listy_by_autoids(autoids=autoids)
        autoids = [i.autoid for i in origin_orders]
        items = await ItemsService(db_session=self.db_session).group_by_order_annotated_statistics(autoids=autoids)
        sales_order = await SalesOrdersService(db_session=self.db_session).list_by_orders(autoids=autoids)
        items_statistic_data = {i.order: i for i in items}
        sales_order_data = {i.order: i for i in sales_order}
        for origin_order in origin_orders:
            if item := items_statistic_data.get(origin_order.autoid):
                origin_order.completed = item.completed
            if order := sales_order_data.get(origin_order.autoid):
                origin_order.sales_order = order
        return [ArinvRelatedArinvDetSchema.from_orm(i).model_dump() for i in origin_orders]



