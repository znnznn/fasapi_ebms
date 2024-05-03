from origin_db.services import OriginOrderService, OriginItemService
from websockets_connection.managers import connection_manager

subscribe_mapper = {
    "orders": OriginOrderService,
    "items": OriginItemService,
}


async def publish(subscribe: str, message: dict):
    await connection_manager.pubsub_client.publish(subscribe, message)
