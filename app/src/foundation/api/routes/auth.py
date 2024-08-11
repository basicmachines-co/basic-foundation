from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from foundation.api.deps import access_token_security, CurrentUser
from foundation.api.routes.schemas import AuthToken, AuthTokenPayload, Message, UserPublic, NewPassword
from foundation.core.config import settings
from foundation.core.deps import UserRepositoryDep
from foundation.core.emails import generate_reset_password_email, send_email
from foundation.core.security import generate_password_reset_token, verify_password_reset_token
from foundation.users import services as user_service
from foundation.users.services import authenticate, UserNotFoundError

router = APIRouter()


@router.post("/login/access-token")
async def login_access_token(
        user_repository: UserRepositoryDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> AuthToken:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await authenticate(
        repository=user_repository, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return AuthToken(
        access_token=access_token_security.create_access_token(subject=jsonable_encoder(AuthTokenPayload(id=user.id)),
                                                               expires_delta=access_token_expires)
    )


@router.post("/login/test-token", response_model=UserPublic)
async def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
async def recover_password(user_repository: UserRepositoryDep, email: str) -> Message:
    """
    Password Recovery

    Sends an email with a password reset token to the address provided if a user is found.
    """

    try:
        user = await user_service.get_user_by_email(repository=user_repository, email=email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    send_email(
        email_to=user.email,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
    return Message(message="Password recovery email sent")


@router.post("/password-reset/")
async def reset_password(user_repository: UserRepositoryDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    try:
        user = await user_service.get_user_by_email(repository=user_repository, email=email)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e.args,
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    updated_user = await user_service.update_user(repository=user_repository, user_id=user.id, update_dict={
        "password": body.new_password,
    })

    return Message(message=f"Password updated successfully for user {updated_user.email}")
