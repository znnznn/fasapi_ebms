from fastapi import APIRouter, WebSocket, Depends, WebSocketException
from starlette.websockets import WebSocketDisconnect

from common.utils import DateValidator
from users.models import User
from websockets_connection.auth import get_auth_user_by_websocket
from websockets_connection.managers import connection_manager

router = APIRouter()


@router.websocket("/orders/")
async def websocket_endpoint_order(websocket: WebSocket, user: User = Depends(get_auth_user_by_websocket)):
    await connection_manager.connect(websocket, "orders")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except (WebSocketException, WebSocketDisconnect):
        await connection_manager.disconnect(websocket, "orders")
        return


@router.websocket("/items/")
async def websocket_endpoint_items(websocket: WebSocket, user: User = Depends(get_auth_user_by_websocket)):
    await connection_manager.connect(websocket, "items")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except (WebSocketException, WebSocketDisconnect):
        await connection_manager.disconnect(websocket, "items")
        return


@router.websocket("/calendar/{category_name}/{year}/{month}/")
async def websocket_endpoint_calendar(
        year: int, month: int, category_name: str,
        websocket: WebSocket, user: User = Depends(get_auth_user_by_websocket)):
    DateValidator.validate_year(year)
    DateValidator.validate_month(month)
    await connection_manager.connect(websocket, f'calendar-{category_name}-{year}-{month}')
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except (WebSocketException, WebSocketDisconnect):
        await connection_manager.disconnect(websocket, f'calendar-{category_name}-{year}-{month}')
        return
