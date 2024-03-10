from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
from fastapi_users import exceptions, BaseUserManager, models
from fastapi_users.manager import UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from database import get_async_session, get_user_db
from users.manager import get_user_manager
from users.mixins import is_admin_user
from users.models import User
from users.schemas import UserRead, UsersPaginatedSchema, PasswordResetConfirmationSchema
from users.services import UserService

router = APIRouter()

RESET_PASSWORD_RESPONSES: OpenAPIResponseType = {
    status.HTTP_400_BAD_REQUEST: {
        "model": ErrorModel,
        "content": {
            "application/json": {
                "examples": {
                    ErrorCode.RESET_PASSWORD_BAD_TOKEN: {
                        "summary": "Bad or expired token.",
                        "value": {"detail": ErrorCode.RESET_PASSWORD_BAD_TOKEN},
                    },
                    ErrorCode.RESET_PASSWORD_INVALID_PASSWORD: {
                        "summary": "Password validation failed.",
                        "value": {
                            "detail": {
                                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                                "reason": "Password should be at least 3 characters",
                            }
                        },
                    },
                }
            }
        },
    },
}


@router.get("/", response_model=UsersPaginatedSchema, tags=["users"])
async def get_users(limit=10, offset=0, user_service: UserService = Depends(get_user_db)):
    return await user_service.paginated_list(limit=limit, offset=offset)


@router.post(
    "/password-reset",
    status_code=status.HTTP_202_ACCEPTED,
    name="reset:forgot_password",
)
async def forgot_password(
        request: Request,
        email: EmailStr = Body(..., embed=True),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    try:
        user = await user_manager.get_by_email(email)
    except exceptions.UserNotExists:
        return None

    try:
        await user_manager.forgot_password(user, request)
    except exceptions.UserInactive:
        pass

    return None

@router.post(
    "/password-reset-confirm",
    name="reset:reset_password",
    responses=RESET_PASSWORD_RESPONSES,
)
async def reset_password(
        request: Request,
        confirmation: PasswordResetConfirmationSchema,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    token = confirmation.token
    password = confirmation.new_password1
    try:
        await user_manager.reset_password(token, password, request)
    except (
            exceptions.InvalidResetPasswordToken,
            exceptions.UserNotExists,
            exceptions.UserInactive,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.RESET_PASSWORD_BAD_TOKEN,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.RESET_PASSWORD_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
