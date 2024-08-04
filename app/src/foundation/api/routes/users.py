from typing import Any

from fastapi import Response, APIRouter, Depends

from foundation.api.deps import JwtAuthorizationCredentialsDep, get_current_active_superuser
from foundation.api.routes.schemas import UsersPublic
from foundation.core.deps import UserRepositoryDep
from foundation.core.security import access_token_security

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


## new user routes

@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def read_users(user_repository: UserRepositoryDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """

    count = await user_repository.count()
    users = await user_repository.find_all(skip, limit)
    return UsersPublic(data=users, count=count)
