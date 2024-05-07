import asyncio
import json
from typing import List
import redis.asyncio as aioredis
from broadcaster import Broadcast

from fastapi import WebSocket
from starlette.websockets import WebSocketState

from database import redis_pool
from settings import REDIS_URL


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
    broadcaster = Broadcast(url=REDIS_URL)

    def __init__(self):
        self.active_connections: dict[str, List[WebSocket]] = {}
        self.pubsub_client = RedisPubSubManager()

    async def connect_broadcaster(self):
        await self.broadcaster.connect()

    async def disconnect_broadcaster(self):
        await self.broadcaster.disconnect()

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
            subscribe_n_listen_task = asyncio.create_task(
                self._subscribe_and_listen_to_channel(
                    subscribe=subscribe, ws=websocket
                )
            )
            wait_for_subscribe_task = asyncio.create_task(
                asyncio.sleep(1)
            )  # 1 Second delay

            # This coroutine would be exited when the time elaps, that should be anough time for the
            # Subscription task to be done
            await asyncio.wait(
                [subscribe_n_listen_task, wait_for_subscribe_task],
                return_when=asyncio.FIRST_COMPLETED,
            )

    async def disconnect_all(self, subscribe: str):
        self.active_connections[subscribe] = []

    async def get_active_connections(self, subscribe: str) -> List[WebSocket]:
        if connections := self.active_connections.get(subscribe):
            print("---------------------connections----------------------")
            print(connections)
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
                    message = json.loads(message["data"].decode("utf-8"))
                    subscribe = message["channel"].decode("utf-8")
                    await self._consume_events(subscribe=subscribe, message=message)
        except Exception as exc:
            print(exc)

    async def _subscribe_and_listen_to_channel(self, subscribe: str, ws: WebSocket):

        async with self.broadcaster.subscribe(channel=subscribe) as subscriber:

            count = 0

            async for event in subscriber:
                if count <= 0:
                    message = event.message

                    message_dict = json.loads(message)

                    await self._consume_events(subscribe=subscribe, message=message_dict)
            count += 1

    async def _consume_events(self, subscribe: str, message: dict):
        """
        Function to consume a message and send to all connect clients in all processes
        """
        print("==========_consume_events============")

        room_connections = self.active_connections.get(subscribe)
        if room_connections:
            for connection in room_connections:
                if connection.client_state == WebSocketState.CONNECTED:
                    await self._send_message_to_ws_connection(
                        message=message,
                        ws_connection=connection,
                    )

    async def send_message_to_room(self, subscribe: str, message: dict):
        # Send events to the room

        await self.broadcaster.publish(
            channel=subscribe, message=message
        )

    async def _send_message_to_ws_connection(
            self, message: dict, ws_connection: WebSocket
    ):
        print("==========_send_message_to_ws_connection============")
        print(ws_connection)
        await ws_connection.send_json(data=message)


connection_manager = ConnectionManager()
