from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from foundation.api.deps import access_token_security_bearer, CurrentUserDep
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

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
        user_service: UserServiceDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> AuthToken:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
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
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(user_service: UserServiceDep, email: str) -> Message:
    """
    Password Recovery

    Sends an email with a password reset token to the address provided if a user is found.
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
    Reset password
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
    if not user.is_active:
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
