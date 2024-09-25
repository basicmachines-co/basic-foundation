from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from modules.foundation.api.deps import (
    validate_is_superuser,
    CurrentUserDep,
    AdminRequired,
)
from foundation.users.deps import UserServiceDep
from foundation.users.schemas import (
    UsersPublic,
    UserPublic,
    UserCreate,
    UserUpdate,
    Message,
)
from foundation.users.services import UserNotFoundError, UserValueError, UserCreateError

router = APIRouter()


@router.get(
    "/",
    dependencies=[AdminRequired],
    response_model=UsersPublic,
)
async def get_users(
    user_service: UserServiceDep, skip: int = 0, limit: int = 100
) -> Any:
    """
    Get all users.
    """

    count, users = await user_service.get_users(skip=skip, limit=limit)
    return UsersPublic(data=users, count=count)  # pyright: ignore [reportArgumentType]


@router.get(
    "/{user_id}",
    response_model=UserPublic,
)
async def get_user(
    user_service: UserServiceDep, user_id: UUID, current_user: CurrentUserDep
) -> Any:
    """
    Get a user.
    If the current_user is a non-superuser, they can only get their own user.
    Superusers can get any user.
    """

    if current_user.id != user_id:
        validate_is_superuser(current_user)

    try:
        user = await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    return user


@router.get(
    "/email/{email}",
    response_model=UserPublic,
)
async def get_user_by_email(
    user_service: UserServiceDep, email: str, current_user: CurrentUserDep
) -> Any:
    """
    Get a user.
    """

    validate_is_superuser(current_user)

    try:
        user = await user_service.get_user_by_email(email=email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    return user


@router.post(
    "/",
    dependencies=[AdminRequired],
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(*, user_service: UserServiceDep, user_in: UserCreate) -> Any:
    """
    Create new user.
    """
    try:
        user_created = await user_service.create_user(create_dict=user_in.model_dump())
    except UserCreateError as e:
        raise HTTPException(status_code=400, detail=e.args)
    return user_created


@router.patch(
    "/{user_id}",
    response_model=UserPublic,
)
async def update_user(
    *,
    user_service: UserServiceDep,
    user_id: UUID,
    user_in: UserUpdate,
    current_user: CurrentUserDep,
) -> Any:
    """
    Update a user.
    If the current_user is a non-super user, they can only update their own user.
    Superusers can update any user.
    """
    if current_user.id != user_id:
        validate_is_superuser(current_user)

    try:
        await user_service.get_user_by_id(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )

    try:
        user_updated = await user_service.update_user(
            user_id=user_id, update_dict=user_in.model_dump()
        )
    except UserValueError:
        raise HTTPException(
            status_code=400,
            detail=f"unable to update user with id {user_id}",
        )
    return user_updated


@router.delete(
    "/{user_id}",
)
async def delete_user(
    *, user_service: UserServiceDep, user_id: UUID, current_user: CurrentUserDep
) -> Message:
    """
    Delete a user.
    If the current_user is a non-super user, they can only delete their own user.
    Superusers can delete any other user.
    Superusers can not delete their own user.
    """
    if current_user.id != user_id:
        validate_is_superuser(current_user)

    try:
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    return Message(message=f"user {user_id} deleted")
