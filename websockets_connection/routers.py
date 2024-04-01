from fastapi import APIRouter, WebSocket

from websockets_connection.managers import connection_manager

router = APIRouter(prefix="/ws", tags=["websockets_connection"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket, "orders")
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
