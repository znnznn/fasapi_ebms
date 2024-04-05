from collections import defaultdict
from typing import List

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, subscribe: str):
        print("connect")
        await websocket.accept(subprotocol=websocket.headers.get("sec-websocket-protocol"))
        self.active_connections[subscribe].append(websocket)

    async def disconnect_all(self, subscribe: str):
        self.active_connections[subscribe] = []

    async def get_active_connections(self, subscribe: str) -> List[WebSocket]:
        if connections := self.active_connections.get(subscribe):
            return connections
        return []

    async def disconnect(self, websocket: WebSocket, subscribe: str):
        connections = self.active_connections[subscribe]
        if connections:
            self.active_connections[subscribe].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, subscribe: str):
        print("broadcast")
        data = {"subscribe": subscribe}
        connections = await self.get_active_connections(subscribe)
        for connection in connections:
            await connection.send_json(data)


connection_manager = ConnectionManager()
