from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from fastapi_jwt.jwt import JwtAccess
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


## security
# Read access token from bearer header and cookie (bearer priority)
access_token_security = JwtAccessBearer(
    secret_key=settings.jwt_secret,
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# Read refresh token from bearer header only
refresh_token_security = JwtRefreshBearer(
    secret_key=settings.jwt_secret,
    auto_error=True  # automatically raise HTTPException: HTTP_401_UNAUTHORIZED
)

# reset token for emails
reset_token = JwtAccess(
    secret_key=settings.jwt_secret,
)
