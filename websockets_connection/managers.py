from collections import defaultdict
from typing import List

from fastapi import WebSocket
from sqlalchemy.ext.asyncio import AsyncSession

from common.constants import InputSchemaType
from origin_db.schemas import CategorySchema
from origin_db.services import CategoryService


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, subscribe: str):
        await websocket.accept()
        self.active_connections[subscribe].append(websocket)

    def disconnect(self, websocket: WebSocket, subscribe: str):
        self.active_connections[subscribe].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, subscribe: str, session: AsyncSession):
        objects = await CategoryService(db_session=session).paginated_list()
        data = CategorySchema(**objects).model_json_schema()
        print(data)
        print("*******************************************")
        for connection in self.active_connections[subscribe]:
            await connection.send_json(data)


connection_manager = ConnectionManager()
