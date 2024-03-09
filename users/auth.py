from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi_users import models
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend, Transport, Strategy
from fastapi_users.types import DependencyCallable
from pydantic import BaseModel
from starlette.responses import Response, JSONResponse

from users.manager import SECRET
from users.schemas import UserRead


class BearerResponseRefresh(BaseModel):
    access: str
    refresh: str
    user: UserRead


class BearerTransportRefresh(BearerTransport):
    async def get_login_response(self, token: str, refresh_token: str, user: models.UP) -> Response:
        bearer_response = BearerResponseRefresh(
            access=token,
            refresh=refresh_token,
            token_type="bearer",
            user=user,
        )
        return JSONResponse(bearer_response.model_dump())


class AuthenticationBackendRefresh(AuthenticationBackend):
    def __init__(
            self,
            name: str,
            transport: BearerTransportRefresh,
            get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
            get_refresh_strategy: DependencyCallable[Strategy[models.UP, models.ID]]
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
            self,
            strategy: Strategy[models.UP, models.ID],
            user: models.UP,
    ) -> Response:
        print(user)
        token = await strategy.write_token(user)
        refresh_strategy = self.get_refresh_strategy()
        refresh_token = await refresh_strategy.write_token(user)
        return await self.transport.get_login_response(token=token, refresh_token=refresh_token, user=user)


bearer_transport = BearerTransportRefresh(tokenUrl="token/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=259200)


auth_backend_refresh = AuthenticationBackendRefresh(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
)

