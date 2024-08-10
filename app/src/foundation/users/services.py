from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from foundation.api.routes.schemas import UserCreate, UserUpdate
from foundation.core.repository import Repository
from foundation.core.security import verify_password, get_password_hash
from foundation.users.models import User


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    def __init__(self, id_val: UUID | str):
        super().__init__(f"user {id_val} does not exist")


async def get_user_by_id(*, repository: Repository[User], user_id: UUID) -> User | None:
    user = await repository.find_by_id(user_id)
    if not user:
        error = UserNotFoundError(user_id)
        logger.info(error)
        raise error
    return user


async def get_user_by_email(*, repository: Repository[User], email: str) -> User | None:
    stmt = select(User).where(email == User.email)
    user = await repository.find_one(stmt)
    if not user:
        error = UserNotFoundError(email)
        logger.info(error)
        raise error
    return user


async def authenticate(*, repository: Repository[User], email: str, password: str) -> User | None:
    """
    Finds a user by email and validates the provided password.
    :return: None if either not found or the password is not verified. This prevents the caller from guessing emails.
    """
    try:
        user = await get_user_by_email(repository=repository, email=email)
    except UserNotFoundError:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user(*, repository: Repository[User], user_create: UserCreate) -> User:
    user_data = user_create.model_dump()
    user_data.update({"hashed_password": get_password_hash(user_create.password)})
    try:
        return await repository.create(user_data)
    except IntegrityError as e:
        logger.info(f"error creating user: {e}")
        return None


async def update_user(*, repository: Repository[User], user_id: UUID, user_update: UserUpdate) -> User:
    user_data = user_update.model_dump(exclude_unset=True)
    if user_data.get("password"):
        user_data.update({"hashed_password": get_password_hash(user_data.get("password"))})
    try:
        return await repository.update(user_id, user_data)
    except IntegrityError as e:
        logger.info(f"error updating user: {e}")
        return None
