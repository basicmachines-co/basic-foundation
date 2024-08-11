from typing import Any, List
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from foundation.core.repository import Repository
from foundation.core.security import verify_password, get_password_hash
from foundation.users.models import User


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, id_val: UUID | str):
        super().__init__(f"user {id_val} does not exist")


class UserValueError(Exception):
    """Raised when a user can not be updated."""

    def __init__(self, id_val: UUID):
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

    async def create_user(self, *, create_dict: dict[str, Any]) -> User:
        create_dict.update({"hashed_password": get_password_hash(create_dict.get("password"))})
        try:
            return await self.repository.create(create_dict)
        except IntegrityError as e:
            logger.info(f"error creating user: {e}")
            return None

    async def update_user(self, *, user_id: UUID, update_dict: dict[str, Any]) -> User:
        if update_dict.get("password"):
            update_dict.update({"hashed_password": get_password_hash(update_dict.get("password"))})
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
