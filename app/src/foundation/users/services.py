from loguru import logger
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from foundation.api.routes.schemas import UserCreate
from foundation.core.repository import Repository
from foundation.core.security import verify_password, get_password_hash
from foundation.users.models import User


async def get_user_by_email(*, repository: Repository[User], email: str) -> User | None:
    stmt = select(User).where(email == User.email)
    user = await repository.find_one(stmt)
    return user


async def authenticate(*, repository: Repository[User], email: str, password: str) -> User | None:
    user = await get_user_by_email(repository=repository, email=email)
    if not user:
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
