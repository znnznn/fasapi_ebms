from collections import defaultdict
from typing import List

from fastapi import WebSocket, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants import InputSchemaType
from database import async_session_maker, get_async_session
from origin_db.schemas import CategorySchema, CategoryPaginateSchema
from origin_db.services import CategoryService
from users.auth import get_jwt_strategy, auth_backend_refresh
from users.manager import get_user_manager
from websockets_connection.auth import get_auth_user_by_websocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, subscribe: str):
        print("connect")
        await websocket.accept(subprotocol=websocket.headers.get("sec-websocket-protocol"))
        self.active_connections[subscribe].append(websocket)

    async def disconnect(self, websocket: WebSocket, subscribe: str):
        print("disconnect")
        self.active_connections[subscribe].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, subscribe: str):
        print("broadcast")
        data = {"subscribe": subscribe}
        for connection in self.active_connections[subscribe]:
            await connection.send_json(data)


connection_manager = ConnectionManager()
