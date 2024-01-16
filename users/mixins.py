from fastapi_users import FastAPIUsers

from users.auth import auth_backend
from users.manager import get_user_manager
from users.models import User


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(optional=True)
