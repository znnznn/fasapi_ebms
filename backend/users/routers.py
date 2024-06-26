from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Body
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions, BaseUserManager, models, schemas
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router import ErrorCode
from fastapi_users.router.common import ErrorModel
from pydantic import EmailStr
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from common.constants import Role
from database import get_user_db
from settings import TOKEN_CREDENTIAL
from users.manager import get_user_manager
from users.mixins import is_owner_profile_or_admin, active_user_with_permission, is_owner_profile, IsAuthenticatedAs
from users.schemas import (
    UserRead, UsersPaginatedSchema, PasswordResetConfirmationSchema, UserCreate, UserReadShortSchema, UserUpdate, UserPasswordChangeSchema
)
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


@router.get('/all/', name="users:all", response_model=List[UserRead], tags=["users"])
async def get_users_all(user_service: UserService = Depends(get_user_db), user=Depends(active_user_with_permission)):
    return await user_service.list()


@router.get("/", response_model=UsersPaginatedSchema, tags=["users"])
async def get_users(
        limit=10, offset=0, user_service: UserService = Depends(get_user_db), user=Depends(active_user_with_permission)
):
    return await user_service.paginated_list(limit=limit, offset=offset)


@router.post("/password-reset/", status_code=status.HTTP_202_ACCEPTED, name="reset:forgot_password", )
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


@router.post("/password-reset-confirm/{uid64}/{token}/", name="reset:reset_password", responses=RESET_PASSWORD_RESPONSES)
async def reset_password(
        uid64: str,
        token: str,
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


@router.post(
    "/",
    response_model=UserReadShortSchema,
    status_code=status.HTTP_201_CREATED,
    name="register:register",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.REGISTER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                              "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def register(
        request: Request,
        user_create: UserCreate,  # type: ignore
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        user=Depends(IsAuthenticatedAs(Role.ADMIN)),
):
    try:
        created_user = await user_manager.create(
            user_create, safe=True, request=request
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )

    return schemas.model_validate(UserReadShortSchema, created_user)


# get_current_active_user = authenticator.current_user(
#     active=True, verified=requires_verification
# )
# get_current_superuser = authenticator.current_user(
#     active=True, verified=requires_verification, superuser=True
# )


async def get_user_or_404(
        id: int,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
) -> models.UP:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


@router.get(
    "/{id}/",
    response_model=UserReadShortSchema,
    # dependencies=[Depends(get_current_superuser)],
    name="users:user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a owner profile or not admin.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def get_user(id: int, user=Depends(is_owner_profile_or_admin), instance: models.UP = Depends(get_user_or_404)):
    return schemas.model_validate(UserReadShortSchema, instance)


@router.patch(
    "/{id}/",
    response_model=UserReadShortSchema,
    name="users:patch_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a owner profile or not admin.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS: {
                            "summary": "A user with this email already exists.",
                            "value": {
                                "detail": ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS
                            },
                        },
                        ErrorCode.UPDATE_USER_INVALID_PASSWORD: {
                            "summary": "Password validation failed.",
                            "value": {
                                "detail": {
                                    "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                                    "reason": "Password should be"
                                              "at least 3 characters",
                                }
                            },
                        },
                    }
                }
            },
        },
    },
)
async def update_user(
        id: int,
        user_update: UserUpdate,
        request: Request,
        user=Depends(is_owner_profile_or_admin),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        instance: models.UP = Depends(get_user_or_404),
):
    safe = True
    if user.role_name == Role.ADMIN:
        safe = False
    try:
        user = await user_manager.update(
            user_update, instance, safe=safe, request=request
        )
        return schemas.model_validate(UserReadShortSchema, user)
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.UPDATE_USER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_EMAIL_ALREADY_EXISTS,
        )


@router.delete(
    "/{id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    name="users:delete_user",
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Missing token or inactive user.",
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Not a owner profile or not admin.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)
async def delete_user(
        id: int,
        request: Request,
        user=Depends(is_owner_profile_or_admin),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        instance: models.UP = Depends(get_user_or_404),
):
    await user_manager.delete(instance, request=request)
    return None


@router.post('/{id}/password-change/', name="users:password_change")
async def password_change(
        user_update: UserPasswordChangeSchema,
        user=Depends(is_owner_profile),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager)
):
    if user_update.new_password1 != user_update.new_password2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.UPDATE_USER_INVALID_PASSWORD
        )
    credentials = OAuth2PasswordRequestForm(username=user.email, password=user_update.old_password)
    user = await user_manager.authenticate(credentials)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='The new password is not the same.'
        )
    updated_user = await user_manager._update(user, {"password": user_update.new_password1})
    return schemas.model_validate(UserReadShortSchema, updated_user)


@router.post('/create-admin/{token}/', name="users:admin")
async def create_user(
        token: str,
        user_create: UserCreate,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
):
    if token != TOKEN_CREDENTIAL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not admin."
        )
    try:
        user = await user_manager.create(user_create, safe=False)
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
        )
    except exceptions.InvalidPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                "reason": e.reason,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e,
        )
    return schemas.model_validate(UserReadShortSchema, user)
