import uuid

from fastapi import Depends
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
    CookieTransport,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from basic_api.config import SECRET
from basic_api.deps import get_async_session
from basic_api.users.managers import UserManager
from basic_api.users.models import User

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")
cookie_transport = CookieTransport(cookie_max_age=3600)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


jwt_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
cookie_backend = AuthenticationBackend(
    name="cookie",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)


async def get_cookie_backend():
    yield cookie_backend


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Retrieve the fastapi-users SQLAlchemyUserDatabase for the provided session.

    :param session: The asynchronous session used to interact with the database.
    :return: The SQLAlchemyUserDatabase instance.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager, [jwt_backend, cookie_backend]
)

current_active_user = fastapi_users.current_user(active=True)
current_optional_user = fastapi_users.current_user(optional=True)
