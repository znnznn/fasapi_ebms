from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, models
from fastapi_users.authentication import Strategy
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from users.auth import auth_backend_refresh, RefreshTokenResponse, AccessTokenRefreshResponse
from users.manager import get_user_manager
from users.mixins import active_user_with_permission


router = APIRouter()


login_responses: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.LOGIN_BAD_CREDENTIALS: {
                        "summary": "Bad credentials or the user is inactive.",
                        "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                    },
                    ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                        "summary": "The user is not verified.",
                        "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                    },
                }
            }
        },
    },
    **auth_backend_refresh.transport.get_openapi_login_responses_success(),
}


@router.post("/", name=f"auth:{auth_backend_refresh.name}.login", responses=login_responses)
async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(auth_backend_refresh.get_strategy),
):
    user = await user_manager.authenticate(credentials)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )
    response = await auth_backend_refresh.login(strategy, user)
    await user_manager.on_after_login(user, request, response)
    return response


@router.post("/refresh", name=f"auth:{auth_backend_refresh.name}.logout", response_model=AccessTokenRefreshResponse)
async def refresh(
        response: Response, refresh_token: RefreshTokenResponse, refresh_strategy=Depends(auth_backend_refresh.get_refresh_strategy),
        user_manager=Depends(get_user_manager)
):
    user = await refresh_strategy.read_token(refresh_token.refresh, user_manager)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The refresh token is not valid."
        )
    strategy = auth_backend_refresh.get_strategy()
    token = await strategy.write_token(user)
    return AccessTokenRefreshResponse(access=token, refresh=refresh_token.refresh)
