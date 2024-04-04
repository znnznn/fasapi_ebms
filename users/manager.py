import re
import secrets
import string
from typing import Optional, Union

import jwt
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import BaseUserManager, IntegerIDMixin, models, InvalidPasswordException, exceptions
from fastapi_users.jwt import generate_jwt, decode_jwt
from passlib.handlers.django import django_pbkdf2_sha256
from starlette.responses import Response

from common.constants import Role
from database import get_user_db
from settings import SECRET_KEY
from .models import User
from .schemas import UserCreate
from .utils import EmailSender

SECRET = SECRET_KEY


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def get_forgot_password_token(self, user):
        token_data = {
            "sub": str(user.id),
            "password_fgpt": self.password_helper.hash(user.password),
            "aud": self.reset_password_token_audience,
        }
        token = generate_jwt(
            token_data,
            self.reset_password_token_secret,
            self.reset_password_token_lifetime_seconds,
        )
        return token

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
        if not user_create.password:
            user_create.password = str(
                str(secrets.token_hex(8)) + str(secrets.choice(string.digits))
                + str(secrets.choice(string.punctuation) + str(secrets.choice(string.ascii_uppercase))),
            )
        await self.validate_password(user_create.password, user_create)

        existing_user = await self.user_db.get_by_email(user_create.email)
        if existing_user is not None:
            raise exceptions.UserAlreadyExists()

        user_dict = (
            user_create.create_update_dict()
            if safe
            else user_create.create_update_dict_superuser()
        )
        password = user_dict.pop("password", "")
        user_dict["password"] = self.password_helper.hash(password)
        if not safe:
            user_dict["role"] = Role.ADMIN
        else:
            user_role = user_dict.get("role", Role.WORKER)
            if user_role == Role.ADMIN:
                user_dict["role"] = Role.WORKER

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

    async def forgot_password(
            self, user: models.UP, request: Optional[Request] = None
    ) -> None:
        if not user.is_active:
            raise exceptions.UserInactive()

        token = await self.get_forgot_password_token(user)
        await self.on_after_forgot_password(user, token, request)

    async def reset_password(
            self, token: str, password: str, request: Optional[Request] = None
    ) -> models.UP:
        try:
            data = decode_jwt(
                token,
                self.reset_password_token_secret,
                [self.reset_password_token_audience],
            )
        except jwt.PyJWTError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            user_id = data["sub"]
            password_fingerprint = data["password_fgpt"]
        except KeyError:
            raise exceptions.InvalidResetPasswordToken()

        try:
            parsed_id = self.parse_id(user_id)
        except exceptions.InvalidID:
            raise exceptions.InvalidResetPasswordToken()

        user = await self.get(parsed_id)

        valid_password_fingerprint, _ = self.password_helper.verify_and_update(
            user.password, password_fingerprint
        )
        if not valid_password_fingerprint:
            raise exceptions.InvalidResetPasswordToken()

        if not user.is_active:
            raise exceptions.UserInactive()

        updated_user = await self._update(user, {"password": password})

        await self.on_after_reset_password(user, request)

        return updated_user

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")
        token = await self.get_forgot_password_token(user)
        EmailSender().send_email_invite_new_user(request=request, obj_user=user, token=token)

    async def on_after_forgot_password(
            self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgot their password. Reset token: {token}")
        EmailSender().send_email_reset_password(request=request, obj_user=user, token=token)

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
