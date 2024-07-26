from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi import Response, APIRouter
from fastapi import Security
from fastapi_jwt import JwtAuthorizationCredentials, JwtAccessBearer, JwtRefreshBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.users.schemas import UsersPublic
from app.deps import get_async_session, get_user_repository
from app.models import User
from app.repository import Repository

## security
# Read access token from bearer header and cookie (bearer priority)
access_token_security = JwtAccessBearer(
    secret_key="secret_key",
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# Read refresh token from bearer header only
refresh_token_security = JwtRefreshBearer(
    secret_key="secret_key",
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

## deps
JwtAuthorizationCredentialsDep = Annotated[JwtAuthorizationCredentials, Security(access_token_security)]
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


async def get_current_user(session: SessionDep, credentials: JwtAuthorizationCredentialsDep) -> User:
    # the "subject" (sub) field of the jwt contains the id PK for the user
    # https://github.com/k4black/fastapi-jwt/issues/13
    user: User | None = await session.get(User, credentials.subject)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


router = APIRouter()


## sample rountes
@router.post("/auth")
def auth():
    subject = {"username": "username", "role": "user"}
    return {"access_token": access_token_security.create_access_token(subject=subject)}


@router.post("/auth_cookie")
def auth(response: Response):
    subject = {"username": "username", "role": "user"}
    access_token = access_token_security.create_access_token(subject=subject)
    access_token_security.set_access_cookie(response, access_token)
    return {"access_token": access_token}


@router.get("/users/me")
def read_current_user(
        credentials: JwtAuthorizationCredentialsDep,
):
    return {"username": credentials["username"], "role": credentials["role"]}


UserRepositoryDep = Annotated[Repository[User], Depends(get_user_repository)]


## new user routes

@router.get(
    "/",
    # dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(user_repository: UserRepositoryDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count = await user_repository.count()
    users = await user_repository.find_all(skip, limit)
    return UsersPublic(data=users, count=count)
