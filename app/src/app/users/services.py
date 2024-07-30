from sqlalchemy import select

from app.core.repository import Repository
from app.core.security import verify_password
from app.users.models import User


async def get_user_by_email(*, repository: Repository[User], email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = await repository.find_one(stmt)
    return user


async def authenticate(*, repository: Repository[User], email: str, password: str) -> User | None:
    user = await get_user_by_email(repository=repository, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
