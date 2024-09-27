from typing import Any, Sequence
from uuid import UUID

from loguru import logger
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from foundation.core.config import settings
from foundation.core.email import (
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


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, id_val: UUID | str):
        super().__init__(f"The user {id_val} does not exist")


class UserCreateError(Exception):
    """Raised when a user can not be created."""

    def __init__(self, email: str):
        super().__init__(f"A user with email {email} already exists")


class UserValueError(Exception):
    """Raised when a user can not be updated."""

    def __init__(self, value: Any = None):
        super().__init__(f"The user can not be updated with value '{value}'")


class UserService:
    """
    Service operations for Users
    """

    repository: Repository[User]
    current_user: User | None

    def __init__(self, repository: Repository[User], current_user: User | None = None):
        self.repository = repository
        self.current_user = current_user

    async def get_users(self, *, skip: int, limit: int) -> tuple[int, Sequence[User]]:
        count = await self.repository.count()
        users = await self.repository.find_all(skip, limit)
        return count, users

    async def get_user_by_id(self, *, user_id: UUID) -> User:
        user = await self.repository.find_by_id(user_id)
        if not user:
            error = UserNotFoundError(user_id)
            logger.info(error)
            raise error
        return user

    async def get_user_by_email(self, *, email: str) -> User:
        stmt = select(User).where(User.email == email)
        user = await self.repository.find_one(stmt)
        if not user:
            error = UserNotFoundError(email)
            logger.info(error)
            raise error
        return user

    async def get_users_count(self) -> int:
        return await self.repository.count()

    async def get_active_users_count(self) -> int:
        query = select(func.count()).select_from(User).filter(User.is_active == True)
        return await self.repository.count(query)

    async def get_admin_users_count(self) -> int:
        query = select(func.count()).select_from(User).filter(User.is_superuser == True)
        return await self.repository.count(query)

    async def create_user(self, *, create_dict: dict[str, Any]) -> User:
        create_dict.update(
            {
                "hashed_password": get_password_hash(create_dict["password"]),
                "is_active": True,
            }
        )
        try:
            user = await self.repository.create(create_dict)
        except IntegrityError as e:
            logger.info(f"error creating user: {e}")
            raise UserCreateError(create_dict["email"]) from e

        if settings.EMAIL_ENABLED and user.email:  # pragma: no cover
            email_data = generate_new_account_email(
                email_to=user.email,
                username=user.email,
                password=create_dict["password"],
            )
            send_email(
                email_to=user.email,
                subject=email_data.subject,
                html_content=email_data.html_content,
            )

        return user

    async def update_user(
        self, *, user_id: UUID, update_dict: dict[str, Any]
    ) -> User | None:
        password = update_dict.get("password")
        if password:
            update_dict.update({"hashed_password": get_password_hash(password)})
        try:
            return await self.repository.update(user_id, update_dict)
        except IntegrityError as e:
            logger.info(f"error updating user: {e}")
            raise UserValueError(update_dict["email"]) from e

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


