from fastapi import APIRouter, WebSocket, Depends, WebSocketException
from starlette.websockets import WebSocketDisconnect

from users.mixins import active_user_with_permission
from users.models import User
from websockets_connection.auth import get_auth_user_by_websocket
from websockets_connection.managers import connection_manager

router = APIRouter()


@router.websocket("/orders/")
async def websocket_endpoint(websocket: WebSocket, user: User = Depends(get_auth_user_by_websocket)):
    await connection_manager.connect(websocket, "orders")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except (WebSocketException, WebSocketDisconnect):
        await connection_manager.disconnect(websocket, "orders")
        return
