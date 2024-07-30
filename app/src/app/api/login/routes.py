from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import access_token_security
from app.api.login.schemas import AuthToken, AuthTokenPayload
from app.config import settings
from app.core.deps import UserRepositoryDep
from app.services import authenticate

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
