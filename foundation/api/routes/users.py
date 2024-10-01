from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from foundation.core.users.deps import UserServiceDep
from foundation.core.users.schemas import (
    UsersPublic,
    UserPublic,
    UserCreate,
    UserUpdate,
    Message,
)
from foundation.core.users.services import (
    UserNotFoundError,
    UserValueError,
    UserCreateError,
)

from foundation.api.deps import (
    validate_role_is_admin,
    CurrentUserDep,
    AdminRequired,
)

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
    Retrieves a list of users with pagination support.

    :param user_service: User service dependency for accessing user data
    :param skip: Number of records to skip (default is 0)
    :param limit: Maximum number of records to return (default is 100)
    :return: A UsersPublic object containing the list of users and count

    Example usage::

        # Assuming 'client' is an instance of TestClient
        response = client.get("/users?skip=0&limit=10")
        users = response.json()

    Note:
    - Requires Admin authorization
    - Ensure 'skip' and 'limit' are non-negative integers
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
    Fetch a user by user ID. Requires the current user to be an admin if fetching details other than their own.

    :param user_service: Dependency to access user-related operations
    :param user_id: Unique identifier of the user to fetch
    :param current_user: Logged-in user making the request
    :return: User details

    :raises HTTPException 404: If the user is not found
    :raises HTTPException 403: If the current user is not an admin and tries to fetch details of a different user
    """

    if current_user.id != user_id:
        validate_role_is_admin(current_user)

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
    Fetches user details by email if the current user has admin privileges.

    :param user_service: Service dependency to fetch user data
    :param email: Email address of the user to be fetched
    :param current_user: Currently authenticated user
    :return: User details in response model format or 404 if user not found

    :raises HTTPException: If user with the given email is not found, raises with status code 404
    """

    validate_role_is_admin(current_user)

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
    Creates a new user using the user data provided. Raises HTTP 400 if user creation fails.

    :param user_service: Dependency injection of UserService
    :param user_in: Data required to create a new user

    :return: Created user object as per UserPublic schema or raises HTTP 400 on error

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
    Update user details.

    :param user_service: Dependency that provides user service methods
    :param user_id: UUID representing the user's ID
    :param user_in: Object containing updated user information
    :param current_user: Dependency that provides the currently authenticated user
    :return: Updated user details
    :raises HTTPException:
        - 404 if user is not found
        - 400 if there is an error updating the user

    """
    if current_user.id != user_id:
        validate_role_is_admin(current_user)

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
    Deletes a user based on user_id if the current user is either the same user or an admin.

    :param user_service: Dependency that provides user-related operations
    :param user_id: UUID of the user to be deleted
    :param current_user: Dependency that provides information about the current authenticated user
    :return: Confirmation message indicating that the user has been deleted

    Raises:
        HTTPException: If the user is not found (404 error)
    """
    if current_user.id != user_id:
        validate_role_is_admin(current_user)

    try:
        await user_service.delete_user(user_id=user_id)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    return Message(message=f"user {user_id} deleted")
