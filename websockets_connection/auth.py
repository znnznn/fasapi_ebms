from typing import MutableMapping, Any

from fastapi import Depends, HTTPException, WebSocket, WebSocketException
from fastapi_users import models, BaseUserManager
from fastapi_users.authentication import Strategy, JWTStrategy
from fastapi_users.router import ErrorCode
from starlette import status
from websockets import AbortHandshake

from database import get_user_db
from users.auth import auth_backend_refresh, AuthenticationBackendRefresh, get_jwt_strategy
from users.manager import get_user_manager, UserManager


# @app.exception_handler(HTTPException)
# async def custom_http_exception_handler(request, exc):
#     if not isinstance(request, WebSocket):
#         return await http_exception_handler(request, exc)
#     websocket = request
#     if websocket.application_state == 1:  # 1 = CONNECTED
#         await websocket.close(code=1008, reason=str(exc))  # 1008 = WS_1008_POLICY_VIOLATION
#         return
#     headers = getattr(exc, "headers") or []
#     await websocket._send({"type": "websocket.http.response.start", "status": exc.status_code, "headers": headers})

# class AuthenticationBackendRefreshWebsocket(WebSocketException):
#     def __init__(self, detail: ErrorCode):
#         self.detail = detail


async def get_auth_user_by_websocket(
        websocket: WebSocket, user_manager: UserManager = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(get_jwt_strategy)
) -> models.UP:
    headers = dict(websocket.scope.get("headers"))
    token = headers.get(b'sec-websocket-protocol', b'doesn\'t exist').decode()
    print(token)
    user = await strategy.read_token(token, user_manager)
    if user is None or not user.is_active:
        raise WebSocketException(status.WS_1002_PROTOCOL_ERROR, "Authentication credentials are not valid.")
    return user
