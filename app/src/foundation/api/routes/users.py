from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from foundation.api.deps import get_current_superuser, validate_is_superuser, CurrentUser
from foundation.api.routes.schemas import UsersPublic, UserPublic, UserCreate, UserUpdate, Message
from foundation.core.config import settings
from foundation.core.deps import UserRepositoryDep
from foundation.core.emails import generate_new_account_email, send_email
from foundation.users import services as user_service

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_superuser)],
    response_model=UsersPublic,
)
async def get_users(user_repository: UserRepositoryDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Get all users.
    """

    count = await user_repository.count()
    users = await user_repository.find_all(skip, limit)
    return UsersPublic(data=users, count=count)


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def get_user(user_repository: UserRepositoryDep, user_id: UUID, current_user: CurrentUser) -> Any:
    """
    Get a user.
    If the current_user is a non-superuser, they can only get their own user.
    Superusers can get any user.
    """

    if current_user.id != user_id:
        validate_is_superuser(current_user)

    user = await user_repository.find_by_id(user_id)
    return user


@router.post(
    "/", dependencies=[Depends(get_current_superuser)], response_model=UserPublic,
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
    response_model=UserPublic,
)
async def update_user(*, user_repository: UserRepositoryDep, user_id: UUID, user_in: UserUpdate,
                      current_user: CurrentUser) -> UserPublic:
    """
    Update a user.
    If the current_user is a non-super user, they can only update their own user.
    Superusers can update any user.
    """
    if current_user.id != user_id:
        validate_is_superuser(current_user)

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


@router.delete(
    "/{user_id}",
)
async def delete_user(*, user_repository: UserRepositoryDep, user_id: UUID, current_user: CurrentUser) -> Message:
    """
    Delete a user.
    If the current_user is a non-super user, they can only delete their own user.
    Superusers can delete any other user.
    Superusers can not delete their own user.
    """
    if current_user.id != user_id:
        validate_is_superuser(current_user)

    deleted = await user_repository.delete(user_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    return Message(message=f"user {user_id} deleted")
