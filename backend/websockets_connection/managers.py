import asyncio
import json
import traceback
from typing import List
import redis.asyncio as aioredis
from broadcaster import Broadcast

from fastapi import WebSocket
from starlette import status
from starlette.websockets import WebSocketState

from database import redis_pool
from settings import REDIS_URL


class RedisPubSubManager:
    def __init__(self):
        self.pubsub = None
        self._redis_conection = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        return aioredis.Redis(connection_pool=redis_pool, decode_responses=True, auto_close_connection_pool=False)

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

    async def publish(self, subscribe: str, message: dict):
        print("========== publish redis manager ============")
        print(subscribe)
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

    async def _check_if_ws_connection_is_still_active(self, ws_connection: WebSocket, message=".") -> bool:
        """
        This function would check if the connection is still active. It tries to send a message
        """

        if not (
                ws_connection.application_state == WebSocketState.CONNECTED and ws_connection.client_state == WebSocketState.CONNECTED):
            return False

        # Try to send a message
        try:
            await ws_connection.send_json({message: ''})
        except RuntimeError:
            return False

        except Exception as e:
            traceback.print_exc()
            return False

        return True

    # def add_connection_count(self, channel_id: str):
    #     count = ws_redis.get_cenus_websocket(channel_id=channel_id)
    #     if count is None:
    #         ws_redis.manage_cenus_websocket(channel_id=channel_id, value=1)
    #     else:
    #         count = int(count) + 1
    #         ws_redis.manage_cenus_websocket(channel_id=channel_id, value=count)

    async def connect(self, websocket: WebSocket, subscribe: str):
        print("connect")
        await websocket.accept(subprotocol=websocket.headers.get("sec-websocket-protocol"))
        # is_connection_active = await self._check_if_ws_connection_is_still_active(websocket, subscribe)
        #
        # if not is_connection_active:
        #     await websocket.close()
        #     return
        if self.active_connections.get(subscribe):
            print("active_connections")
            self.active_connections[subscribe].append(websocket)
        else:
            print("not active_connections")
            self.active_connections[subscribe] = [websocket]
            self.broadcaster.subscribe(channel=subscribe)
        await self.pubsub_client.connect()
        pubsub_subscriber = await self.pubsub_client.subscribe(subscribe)
        await asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber))
        subscribe_n_listen_task = asyncio.create_task(
            self._subscribe_and_listen_to_channel(
                subscribe=subscribe,
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
            return connections
        return []

    async def disconnect(self, websocket: WebSocket, subscribe: str):
        connections = self.active_connections[subscribe]
        if connections:
            self.active_connections[subscribe].remove(websocket)
            connections = self.active_connections[subscribe]
            if len(connections) == 0:
                del self.active_connections[subscribe]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, subscribe: str, data_send: dict = None):
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
                    data = json.loads(message["data"].decode("utf-8"))
                    subscribe = message["channel"].decode("utf-8")
                    await self._consume_events(subscribe=subscribe, message=data)
        except Exception as exc:
            print("pubsub_data_reader error")
            print(exc)

    async def _subscribe_and_listen_to_channel(self, subscribe: str):
        print("subscribe_and_listen_to_channel")

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
                try:
                    await self._send_message_to_ws_connection(
                        message=message,
                        ws_connection=connection,
                        subscribe=subscribe,
                    )
                except Exception as exc:
                    print("consume_events error")
                    print("error", exc)
                    await self.disconnect(websocket=connection, subscribe=subscribe)

    async def send_message_to_room(self, subscribe: str, message: dict):
        # Send events to the room
        print("==========send_message_to_room============")
        print(self.active_connections)

        # await self.broadcaster.publish(
        #     channel=subscribe, message=message
        # )
        await self.pubsub_client.publish(subscribe, message)

    async def _send_message_to_ws_connection(
            self, message: dict, ws_connection: WebSocket, subscribe: str
    ):
        if ws_connection.client_state == WebSocketState.CONNECTED and ws_connection.application_state == WebSocketState.CONNECTED:
            await ws_connection.send_json(data=message)
        else:
            print("Connection not available")
            await self.disconnect(websocket=ws_connection, subscribe=subscribe)


connection_manager = ConnectionManager()
