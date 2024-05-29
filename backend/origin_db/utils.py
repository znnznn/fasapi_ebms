from ebms_api.client import ArinvClient
from origin_db.services import OriginOrderService
from stages.utils import send_data_to_ws


async def send_new_ship_date_to_ebms(model_dump: dict):
    autoids = model_dump.get('autoids')
    ship_date = model_dump.get('ship_date')
    origin_orders = await OriginOrderService().get_origin_order_by_autoids(autoids=autoids)
    await OriginOrderService().update_ship_date(autoids=autoids, ship_date=ship_date)
    await send_data_to_ws('orders', list_autoids=autoids)
    ebms_api_client = ArinvClient()
    for instance in origin_orders:
        response = ebms_api_client.patch(ebms_api_client.retrieve_url(instance.autoid), {"SHIP_DATE": ship_date})
        if response.status_code != 200:
            await OriginOrderService().update_ship_date(autoids=autoids, ship_date=instance.ship_date)
            await send_data_to_ws('orders', autoid=instance.autoid)
