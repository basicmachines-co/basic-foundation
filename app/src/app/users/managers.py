import uuid
from typing import Union, Optional

from app.users.models import User
from fastapi import Request
from fastapi_users import (
    UUIDIDMixin,
    BaseUserManager,
    schemas,
    models,
    InvalidPasswordException,
)

from app import config

SECRET = config.settings.jwt_secret


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    async def validate_password(
            self, password: str, user: Union[schemas.UC, models.UP]
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(reason="Password must be > 3")

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

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
