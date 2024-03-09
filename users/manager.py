import re
from typing import Optional, Union

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, models, InvalidPasswordException, exceptions
from passlib.handlers.django import django_pbkdf2_sha256
from starlette.responses import Response

from database import get_user_db
from settings import SECRET_KEY
from .models import User
from .schemas import UserCreate


SECRET = SECRET_KEY


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def authenticate(self, credentials: OAuth2PasswordRequestForm) -> Optional[models.UP]:
        try:
            user = await self.get_by_email(credentials.username)
        except exceptions.UserNotExists:
            self.password_helper.hash(credentials.password)
            return None
        # is_verified = django_pbkdf2_sha256.verify(credentials.password, user.password)
        is_verified, updated_password_hash = self.password_helper.verify_and_update(
            credentials.password, user.password
        )
        if not is_verified:
            return None
        return user

    async def create(
            self,
            user_create: UserCreate,
            safe: bool = False,
            request: Optional[Request] = None,
    ) -> models.UP:
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password")
        user_dict["password"] = self.password_helper.hash(password)

        created_user = await self.user_db.create(user_dict)

        await self.on_after_register(created_user, request)

        return created_user

    async def validate_password(
            self,
            password: str,
            user: Union[UserCreate, User],
    ) -> None:
        if not bool(re.match("""^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!#"$%&'()*+,-./:;<=>?@[\]^_`{|}~]).{8,128}$""", password)):
            raise InvalidPasswordException(
                reason=
                """ 
                Your password can’t be less than 8 characters, and must contain at least one 
                lowercase letter, uppercase letter, one digit and one special character.
                """
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_login(
            self,
            user: models.UP,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
    ) -> None:
        print(f"User {user.id} logged in.")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
