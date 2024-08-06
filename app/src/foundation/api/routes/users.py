from typing import Any
from uuid import UUID

from fastapi import Response, APIRouter, Depends, HTTPException, status

from foundation.api.deps import JwtAuthorizationCredentialsDep, get_current_active_superuser
from foundation.api.routes.schemas import UsersPublic, UserPublic, UserCreate, UserUpdate
from foundation.core.config import settings
from foundation.core.deps import UserRepositoryDep
from foundation.core.emails import generate_new_account_email, send_email
from foundation.core.security import access_token_security
from foundation.users import services as user_service

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


## end sample routes

@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
async def get_users(user_repository: UserRepositoryDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get all users.
    """

    count = await user_repository.count()
    users = await user_repository.find_all(skip, limit)
    return UsersPublic(data=users, count=count)


@router.post(
    "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
async def create_user(*, user_repository: UserRepositoryDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    user_created = await user_service.create_user(repository=user_repository, user_create=user_in)
    if not user_created:
        raise HTTPException(
            status_code=400,
            detail=f"unable to create user {user_in}",
        )

    if settings.EMAIL_ENABLED and user_in.email:
        email_data = generate_new_account_email(
            email_to=user_in.email, username=user_in.email, password=user_in.password
        )
        send_email(
            email_to=user_in.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return user_created


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
async def update_user(*, user_repository: UserRepositoryDep, user_id: UUID, user_in: UserUpdate) -> Any:
    """
    Update a user.
    """

    user = await user_repository.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    user_updated = await user_service.update_user(repository=user_repository, user_id=user_id, user_update=user_in)
    if not user_updated:
        raise HTTPException(
            status_code=400,
            detail=f"unable to update user with id {user_id}",
        )
    return user_updated
