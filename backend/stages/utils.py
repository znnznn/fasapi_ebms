from common.utils import DateValidator
from origin_db.filters import CategoryFilter
from origin_db.schemas import ArinvDetSchema, ArinvRelatedArinvDetSchema, ArinvDetPaginateSchema
from origin_db.services import OriginItemService, OriginOrderService, CategoryService, InventryService
from stages.services import ItemsService, SalesOrdersService, CapacitiesService
from websockets_connection.services_mapper import publish


class GetDataForSending:

    async def one_origin_item_object(self, autoid: str) -> dict:
        origin_item = await OriginItemService().get_origin_item_with_item(autoid)
        items_statistic = await ItemsService().group_by_item_statistics(autoids=[origin_item.autoid])
        related_items = await ItemsService().get_related_items_by_origin_items(autoids=[origin_item.autoid])
        items_statistic_data = {i.origin_item: i for i in items_statistic}
        items_data = {i.origin_item: i for i in related_items}
        if added_item := items_statistic_data.get(origin_item.autoid):
            origin_item.completed = added_item.completed
        if added_item := items_data.get(origin_item.autoid):
            origin_item.item = added_item
        data = ArinvDetSchema.from_orm(origin_item).model_dump()
        return data

    async def one_origin_order_object(self, autoid: str) -> dict:
        result = await OriginOrderService().get_with_sqlalchemy(autoid=autoid)
        autoids = [result.autoid]
        items = await ItemsService().group_by_order_annotated_statistics(autoids=autoids)
        sales_order = await SalesOrdersService().list_by_orders(autoids=autoids)
        related_items = await ItemsService().get_related_items_by_order(autoids=autoids)
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
                detail.completed = True if item.stage and item.stage.name == 'Done' else False
                detail.item = item
                completed.append(detail.completed)
            else:
                completed.append(False)
        result.completed = all(completed)
        return ArinvRelatedArinvDetSchema.from_orm(result).model_dump()

    async def get_items_by_autoids(self, autoids: list) -> list[dict]:
        origin_items = await OriginItemService().get_list_by_autoids_with_sqlalchemy(autoids=autoids)
        autoids = [i.autoid for i in origin_items]
        items_statistic = await ItemsService().group_by_item_statistics(autoids=autoids)
        related_items = await ItemsService().get_related_items_by_origin_items(autoids=autoids)
        items_statistic_data = {i.origin_item: i for i in items_statistic}
        items_data = {i.origin_item: i for i in related_items}
        for origin_item in origin_items:
            if item := items_statistic_data.get(origin_item.autoid):
                origin_item.completed = item.completed
            if item := items_data.get(origin_item.autoid):
                origin_item.item = item
        return [ArinvDetSchema.from_orm(i).model_dump() for i in origin_items]

    async def get_orders_by_autoids(self, autoids: list) -> list[dict]:
        origin_orders = await OriginOrderService().get_origin_order_by_autoids_with_sqlalchemy(autoids=autoids)
        autoids = [i.autoid for i in origin_orders]
        items = await ItemsService().group_by_order_annotated_statistics(autoids=autoids)
        sales_order = await SalesOrdersService().list_by_orders(autoids=autoids)
        items_statistic_data = {i.order: i for i in items}
        sales_order_data = {i.order: i for i in sales_order}
        for origin_order in origin_orders:
            if item := items_statistic_data.get(origin_order.autoid):
                origin_order.completed = item.completed
            if order := sales_order_data.get(origin_order.autoid):
                origin_order.sales_order = order
        return [ArinvRelatedArinvDetSchema.from_orm(i).model_dump() for i in origin_orders]


async def send_data_to_ws(subscribe: str, autoid: str = None, list_autoids: list = None) -> None:
    data = None
    if list_autoids:
        if subscribe == 'items':
            data = await GetDataForSending().get_items_by_autoids(list_autoids)
            for item in data:
                await publish(subscribe, item)
        elif subscribe == 'orders':
            data = await GetDataForSending().get_orders_by_autoids(list_autoids)
            for item in data:
                await publish(subscribe, item)
        return
    if not autoid:
        return
    elif subscribe == 'items':
        data = await GetDataForSending().one_origin_item_object(autoid)
    elif subscribe == 'orders':
        data = await GetDataForSending().one_origin_order_object(autoid)
    if data:
        await publish(subscribe, data)


async def send_calendars_data_to_ws(year: int, month: int, item_autoid: str) -> None:
    category_filter: CategoryFilter = CategoryFilter()
    origin_item = await OriginItemService().get(autoid=item_autoid)
    category_filter.name = origin_item.category
    list_of_days = DateValidator.get_month_days(year=year, month=month)
    context = {}
    for day in list_of_days:
        context[day] = {}
    categories = await CategoryService(list_filter=category_filter).list()
    categories_data = {c.autoid: c.prod_type for c in categories}
    item_objs = await ItemsService().get_autoids_and_production_date_by_month(year=year, month=month)
    items_data = {i.origin_item: i.production_date for i in item_objs}
    capacities = await CapacitiesService().list()
    items_data = items_data if items_data else []
    total_capacity = await InventryService().count_capacity_by_days(
        items_data=items_data, list_categories=categories_data.values()) if items_data else []
    context['capacity_data'] = {categories_data.get(capacity.category_autoid): capacity.per_day for capacity in capacities}
    if context['capacity_data']:
        for capacity in total_capacity:
            context[capacity.production_date] = {
                capacity.prod_type: {"capacity": float(capacity.total_capacity), "count_orders": capacity.count_orders}
            }
    if context:
        await publish(f'calendar-{origin_item.category}-{year}-{month}', context)

