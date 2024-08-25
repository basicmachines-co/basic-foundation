from typing import Any, List
from uuid import UUID

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Query
from starlette.requests import Request

from foundation.core.config import settings
from foundation.core.emails import (
    generate_new_account_email,
    send_email,
    generate_reset_password_email,
)
from foundation.core.repository import Repository
from foundation.core.security import (
    verify_password,
    get_password_hash,
    generate_password_reset_token,
)
from foundation.users.models import User
from foundation.web.pagination import Paginator


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, id_val: UUID | str):
        super().__init__(f"user {id_val} does not exist")


class UserCreateError(Exception):
    """Raised when a user can not be created."""

    def __init__(self, email: str):
        super().__init__(f"user {email} can not be created")


class UserValueError(Exception):
    """Raised when a user can not be updated."""

    def __init__(self, id_val: UUID | str):
        super().__init__(f"user {id_val} can not be updated")


class UserService:
    """
    Service operations for Users
    """

    repository: Repository[User]

    def __init__(self, repository: Repository[User]):
        self.repository = repository

    async def get_users(self, *, skip: int, limit: int) -> (int, List[User]):
        count = await self.repository.count()
        users = await self.repository.find_all(skip, limit)
        return count, users

    async def get_user_by_id(self, *, user_id: UUID) -> User | None:
        user = await self.repository.find_by_id(user_id)
        if not user:
            error = UserNotFoundError(user_id)
            logger.info(error)
            raise error
        return user

    async def get_user_by_email(self, *, email: str) -> User | None:
        stmt = select(User).where(email == User.email)
        user = await self.repository.find_one(stmt)
        if not user:
            error = UserNotFoundError(email)
            logger.info(error)
            raise error
        return user

    async def get_users_count(self) -> int:
        return await self.repository.count()

    async def get_active_users_count(self) -> int:
        query = select(func.count()).select_from(User).filter(True == User.is_active)
        return await self.repository.count(query)

    async def get_admin_users_count(self) -> int:
        query = select(func.count()).select_from(User).filter(True == User.is_superuser)
        return await self.repository.count(query)

    async def create_user(self, *, create_dict: dict[str, Any]) -> User:
        create_dict.update(
            {
                "hashed_password": get_password_hash(create_dict.get("password")),
                "is_active": True
            }
        )
        try:
            user = await self.repository.create(create_dict)
        except IntegrityError as e:
            logger.info(f"error creating user: {e}")
            raise UserCreateError(create_dict.get("email"))

        if settings.EMAIL_ENABLED and user.email:
            email_data = generate_new_account_email(
                email_to=user.email,
                username=user.email,
                password=create_dict.get("password"),
            )
            send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

        return user

    async def update_user(self, *, user_id: UUID, update_dict: dict[str, Any]) -> User:
        if update_dict.get("password"):
            update_dict.update(
                {"hashed_password": get_password_hash(update_dict.get("password"))}
            )
        try:
            return await self.repository.update(user_id, update_dict)
        except IntegrityError as e:
            logger.info(f"error updating user: {e}")
            raise UserValueError(user_id)

    async def delete_user(self, *, user_id: UUID) -> None:
        deleted = await self.repository.delete(user_id)
        if not deleted:
            error = UserNotFoundError(user_id)
            logger.info(f"error deleting user: {error}")
            raise error

    async def authenticate(self, *, email: str, password: str) -> User | None:
        """
        Finds a user by email and validates the provided password.
        :return: None if either not found or the password is not verified. This prevents the caller from guessing emails.
        """
        try:
            user = await self.get_user_by_email(email=email)
        except UserNotFoundError:
            return None
        if not verify_password(password, user.hashed_password):
            logger.info(f"error verifying password for user: {user.id}")
            return None
        return user

    async def recover_password(self, email: str) -> None:
        """
        Send a passowrd recovery email with a reset token to the supplied email
        :return None
        """
        user = await self.get_user_by_email(email=email)

        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )


class UserPagination:
    repository: Repository[User]

    def __init__(self, repository: Repository[User]):
        self.repository = repository

    def paginate(self, request: Request, query: Query = None, page_size: int = 10):
        return Paginator(request, self.repository, query, page_size)
