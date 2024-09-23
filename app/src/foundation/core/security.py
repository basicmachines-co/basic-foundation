from datetime import timedelta
from typing import TypedDict

from authlib.jose.errors import BadSignatureError
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from fastapi_jwt.jwt import JwtAccess
from fastapi_jwt.jwt_backends.abstract_backend import BackendException
from jwt import InvalidTokenError
from passlib.context import CryptContext

from foundation.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


## security
# Read access token from bearer header and cookie (bearer priority)
access_token_security = JwtAccessBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True,  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# Read refresh token from bearer header only
refresh_token_security = JwtRefreshBearer(
    secret_key=settings.JWT_SECRET,
    auto_error=True,  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# reset token for emails
reset_token = JwtAccess(
    secret_key=settings.JWT_SECRET,
)


class ResetTokenSubject(TypedDict):
    email: str


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    subject = {"email": email}
    return reset_token.create_access_token(subject=subject, expires_delta=delta)


def verify_password_reset_token(token: str) -> str | None:
    try:
        decoded_token = reset_token.jwt_backend.decode(token, settings.JWT_SECRET)
        assert decoded_token is not None
        subject: ResetTokenSubject = decoded_token["subject"]
        return subject.get("email")
    except (InvalidTokenError, BackendException, BadSignatureError):
        return None
