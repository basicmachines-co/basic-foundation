from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from modules.foundation.api.deps import access_token_security_bearer, CurrentUserDep
from foundation.core.config import settings
from foundation.core.security import verify_password_reset_token
from foundation.users.deps import UserServiceDep
from foundation.users.schemas import (
    AuthToken,
    AuthTokenPayload,
    Message,
    UserPublic,
    NewPassword,
)
from foundation.users.services import UserNotFoundError
from foundation.users.models import StatusEnum

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
    user_service: UserServiceDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AuthToken:
    """
    Handles user login and returns access token.

    :param user_service: User service dependency to authenticate user credentials.
    :param form_data: Form data containing user login credentials.
    :return: AuthToken object containing access token.

    Raises:
        HTTPException: If email/password are incorrect or user is inactive.
    """
    user = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.status == StatusEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return AuthToken(
        access_token=access_token_security_bearer.create_access_token(
            subject=jsonable_encoder(AuthTokenPayload(id=user.id)),
            expires_delta=access_token_expires,
        )
    )


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUserDep) -> Any:
    """
    Endpoint to verify the current user's token.

    :param current_user: The user object derived from the current token.
    :return: The current user object.

    Example:
        To verify the user's token, make a POST request to /login/test-token:

        ```
        response = client.post("/login/test-token", headers={"Authorization": "Bearer <token>"})
        ```

        The response will contain the user object if the token is valid.

    Errors:
        - 401 Unauthorized: If the token is missing or invalid.
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(user_service: UserServiceDep, email: str) -> Message:
    """
    Initiates a password recovery process by sending a recovery email to the user.

    :param user_service: Dependency that provides user-related operations.
    :param email: User's email address.
    :return: Message indicating the password recovery email was sent.

    Raises an HTTP 404 error if the user is not found.
    """

    try:
        await user_service.recover_password(email=email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )
    return Message(message="Password recovery email sent")


@router.post("/password-reset/")
async def reset_password(user_service: UserServiceDep, body: NewPassword) -> Message:
    """
    Reset a user's password given a valid reset token, email, and new password.

    :param user_service: Dependency injection for UserService.
    :param body: Object containing the reset token and new password.
    :return: A success message when the password is updated.

    Raises HTTPException with status code 400 if:
    - Token is invalid
    - User is inactive

    Raises HTTPException with status code 404 if:
    - User is not found
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    try:
        user = await user_service.get_user_by_email(email=email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args[0],
        )
    if not user.status == StatusEnum.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")

    updated_user = await user_service.update_user(
        user_id=user.id,
        update_dict={
            "password": body.new_password,
        },
    )
    assert updated_user is not None
    return Message(
        message=f"Password updated successfully for user {updated_user.email}"
    )
