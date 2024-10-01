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
    """
    Verifies if the provided plain text password matches the hashed password.

    :param plain_password: The plain text password to verify.
    :param hashed_password: The hashed password to compare against.
    :return: True if the passwords match, otherwise False.

    Usage example:

        if verify_password("user-input-password", stored_hashed_password):
            print("Password is correct.")
        else:
            print("Password is incorrect.")

    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hashes the provided password using a predefined hashing algorithm.

    :param password: Plain text password to be hashed
    :return: Hashed password

    Example usage:
        hashed_password = get_password_hash("my_password")
    """
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
    """
    ResetTokenSubject is a TypedDict defining the structure of a dictionary that holds a user's email for reset token purposes.

    .. code-block:: python

        reset_token = ResetTokenSubject(email="user@example.com")

    Error cases:
      - Raises KeyError if 'email' key is not present when initializing.
      - Email must be a string.
    """

    email: str


def generate_password_reset_token(email: str) -> str:
    """
    :param email: The email address for which to generate a password reset token.
    :return: A string representing a password reset token.

    Generates a password reset token for the given email. The token is set to expire in the number of hours specified by EMAIL_RESET_TOKEN_EXPIRE_HOURS.

    Example:

        token = generate_password_reset_token("user@example.com")
    """
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    subject = {"email": email}
    return reset_token.create_access_token(subject=subject, expires_delta=delta)


def verify_password_reset_token(token: str) -> str | None:
    """
    Verifies the validity of a password reset token.

    :param token: The JWT token representing password reset details.
    :return: The email address if the token is valid. Returns None if the token is invalid or decoding fails.

    Example:

        email = verify_password_reset_token('some_token_string')
        if email:
            print("Valid token for email:", email)
        else:
            print("Invalid or expired token")

    Error cases:
    - Returns None if the token is invalid, expired, or tampered with.
    - Catches and handles InvalidTokenError, BackendException, BadSignatureError exceptions.
    """
    try:
        decoded_token = reset_token.jwt_backend.decode(token, settings.JWT_SECRET)
        assert decoded_token is not None
        subject: ResetTokenSubject = decoded_token["subject"]
        return subject.get("email")
    except (InvalidTokenError, BackendException, BadSignatureError):
        return None
