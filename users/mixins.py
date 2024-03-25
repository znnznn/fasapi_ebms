from typing import List

from fastapi import Depends, HTTPException
from fastapi_users import FastAPIUsers, BaseUserManager, models, exceptions
from starlette import status

from common.constants import Role
from users.auth import auth_backend_refresh
from users.manager import get_user_manager
from users.models import User


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend_refresh],
)

current_user = fastapi_users.current_user(optional=True)


async def active_user_with_permission(user=Depends(current_user)):
    # At this point, you are sure you have an active user at hand. Otherwise, the `current_active_user` would already have thrown an error
    if not user:
        raise HTTPException(detail="Authentication credentials were not provided.", status_code=status.HTTP_403_FORBIDDEN)
    return user


async def is_admin(user=Depends(active_user_with_permission)):
    if user.role == Role.ADMIN:
        return user
    raise HTTPException(detail="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)


async def is_role(user=Depends(active_user_with_permission), role=List[str]):
    if user.role in role:
        return user
    raise HTTPException(detail="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)


async def is_owner_profile_or_admin(id: int, user=Depends(active_user_with_permission)):
    if user.id == id or user.role == Role.ADMIN:
        return user
    raise HTTPException(detail="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)


async def is_owner_profile(id: int, user=Depends(active_user_with_permission)):
    if user.id == id:
        return user
    raise HTTPException(detail="Permission denied.", status_code=status.HTTP_403_FORBIDDEN)


async def get_user_or_404_by_admin(
        id: str,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        user=Depends(is_admin),
) -> models.UP:
    try:
        parsed_id = user_manager.parse_id(id)
        return await user_manager.get(parsed_id)
    except (exceptions.UserNotExists, exceptions.InvalidID) as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e


class IsAuthenticatedAs:
    def __init__(self, *allowed_roles: str):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(active_user_with_permission)):
        print("user=======>", user)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="You have not a permission to performe action.")
        return user


is_admin_user = IsAuthenticatedAs(Role.ADMIN)

IsAdminOrWorker = IsAuthenticatedAs(Role.ADMIN, Role.WORKER)