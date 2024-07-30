from sqlalchemy import select

from app.models import User
from app.repository import Repository
from app.security import verify_password


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
