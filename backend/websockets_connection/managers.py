import asyncio
import json
from typing import List
import redis.asyncio as aioredis

from fastapi import WebSocket

from database import redis_pool


class RedisPubSubManager:
    def __init__(self):
        self.pubsub = None
        self._redis_conection = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        return aioredis.Redis(connection_pool=redis_pool, decode_responses=True)

    @property
    def redis_connection(self):
        return self._redis_conection

    @redis_connection.setter
    def redis_connection(self, value):
        self._redis_conection = value

    async def connect(self):
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def subscribe(self, subscribe: str) -> aioredis.Redis:
        await self.pubsub.subscribe(subscribe)
        return self.pubsub

    async def unsubscribe(self, subscribe: str):
        await self.pubsub.unsubscribe(subscribe)

    async def publish(self, subscribe: str, message: str):
        if self.redis_connection is None:
            self.redis_connection = await self._get_redis_connection()
        message = json.dumps(message).encode("utf-8")
        await self.redis_connection.publish(subscribe, message)

    async def disconnect(self):
        await self.redis_connection.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
        self.pubsub_client = RedisPubSubManager()

    async def connect(self, websocket: WebSocket, subscribe: str):
        print("connect")
        await websocket.accept(subprotocol=websocket.headers.get("sec-websocket-protocol"))
        if self.active_connections.get(subscribe):
            self.active_connections[subscribe].append(websocket)
        else:
            self.active_connections[subscribe] = [websocket]
            await self.pubsub_client.connect()
            pubsub_subscriber = await self.pubsub_client.subscribe(subscribe)
            await asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber))

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

    async def broadcast(self, subscribe: str, data_send: dict = None):
        print("broadcast")
        data = {"subscribe": subscribe}
        if data_send:
            data = data_send
        connections = await self.get_active_connections(subscribe)
        for connection in connections:
            await connection.send_json(data)

    async def _pubsub_data_reader(self, pubsub_subscriber):
        try:
            while True:
                message = await pubsub_subscriber.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    subscribe = message["channel"].decode("utf-8")
                    sockets = await self.get_active_connections(subscribe)
                    if sockets:
                        for socket in sockets:
                            data = message["data"].decode("utf-8")
                            data = json.loads(data)
                            await socket.send_json(data)
        except Exception as exc:
            print(exc)


connection_manager = ConnectionManager()
