from origin_db.services import OriginOrderService, OriginItemService

subscribe_mapper = {
    "orders": OriginOrderService,
    "items": OriginItemService,
}