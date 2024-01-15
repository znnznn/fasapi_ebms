from fastapi.security import OAuth2AuthorizationCodeBearer
from fastapi_users.authentication import BearerTransport, JWTStrategy, AuthenticationBackend
from pydantic import BaseModel
from starlette.responses import Response, JSONResponse

from users.manager import SECRET


class BearerResponseRefresh(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class BearerTransportRefresh(BearerTransport):
    # def __init__(self, tokenUrl: str):
    #     super().__init__(tokenUrl)
    #     self.scheme = OAuth2AuthorizationCodeBearer
    async def get_login_response(self, token: str, refresh_token: str) -> Response:
        bearer_response = BearerResponseRefresh(
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
        return JSONResponse(bearer_response.model_dump())


bearer_transport = BearerTransportRefresh(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
