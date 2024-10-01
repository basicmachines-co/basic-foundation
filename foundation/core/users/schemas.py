import re
import uuid
from typing import Sequence, Annotated

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, StringConstraints

from foundation.core.users.models import StatusEnum, RoleEnum


class AuthToken(BaseModel):
    """
    AuthToken represents an authentication token.

    Attributes:
        access_token (str): The token string provided upon successful authentication.
        token_type (str): Type of token, default is "bearer".
    """

    access_token: str
    token_type: str = "bearer"


class AuthTokenPayload(BaseModel):
    """
    Represents the payload of an authentication token.

    Attributes:
        id (uuid.UUID): The unique identifier of the authenticated user.

    Raises:
        ValueError: If the 'id' is not a valid UUID.
    """

    id: uuid.UUID


class UserBase(BaseModel):
    """
    Represents a user with properties and validation constraints.

    Attributes:
        email (EmailStr): User's email address.
        status (StatusEnum): Current status of the user, default is PENDING.
        role (RoleEnum): Role assigned to the user, default is USER.
        full_name (Annotated[str, StringConstraints]): Full name of the user with a minimum length of 2 characters.

    Properties:
        is_admin (bool): True if the user has an ADMIN role, False otherwise.
        is_active (bool): True if the user's status is ACTIVE, False otherwise.
    """

    email: EmailStr
    status: StatusEnum = StatusEnum.PENDING
    role: RoleEnum = RoleEnum.USER
    full_name: Annotated[str, StringConstraints(min_length=2)]

    @property
    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    @property
    def is_active(self):
        return self.status == StatusEnum.ACTIVE


def validate_password(password: str) -> str:
    """
    Validates a password based on specific security criteria.
    Ensures:
        - At least 8 characters long
        - Contains at least one uppercase letter
        - Contains at least one lowercase letter
        - Contains at least one digit
        - Contains at least one special character

    Raises ValueError if any condition is not met.

    :param password: The password to validate
    :return: The original password if it passes all checks

    Example:
        >>> validate_password("Valid1Password!")
        'Valid1Password!'
    """
    # Ensure password is at least 8 characters long
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    # Ensure password has at least one uppercase letter
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    # Ensure password has at least one lowercase letter
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")

    # Ensure password has at least one digit
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")

    # Ensure password has at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character.")

    return password


class UserCreate(UserBase):
    """
    Extends UserBase to include password field
    """

    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        return validate_password(value)


class UserRegister(BaseModel):
    """
    Represents a user registration model with necessary fields.

    Fields:
        email: The user's email address, must be a valid email string.
        password: The user's password, as a string.
        full_name: The user's full name, as a string.

    Usage example:

        new_user = UserRegister(email="user@example.com", password="s3cr3t", full_name="John Doe")
    """

    email: EmailStr
    password: str
    full_name: str


class UserUpdate(UserBase):
    """
    UserUpdate class extends UserBase to include an optional password field.

    Attributes
    ----------
    password : str | None
        The password for updating the user. It can be None if not being changed.

    Example usage
    -------------
    user_update = UserUpdate(username="johndoe", email="john@example.com", password="new_password123")

    Error cases
    -----------
    None
    """

    password: str | None


class UserUpdateMe(BaseModel):
    """
    Represents a user's information for updating their own profile.

    Attributes:
        full_name (str | None): The full name of the user. Optional.
        email (EmailStr | None): The email of the user. Optional.

    Example:
        user_update = UserUpdateMe(full_name="John Doe", email="johndoe@example.com")

    Note:
        Each attribute is optional.
    """

    full_name: str | None
    email: EmailStr | None


class UpdatePassword(BaseModel):
    """
    Represents a model to update a user's password.

    Attributes:
        current_password (str): The user's current password.
        new_password (str): The new password to set.

    Example:
        update_pwd = UpdatePassword(current_password="oldPass123", new_password="newPass456")

    Error Cases:
        - Ensure passwords meet criteria such as length and character complexity.
        - Handle potential mismatches or invalid current passwords.
    """

    current_password: str
    new_password: str


class UserPublic(UserBase):
    """
    Represents a public view of a user derived from UserBase.

    Attributes
    ----------
    id : uuid.UUID
        Unique identifier for the user

    Configuration
    -------------
    model_config : ConfigDict
        Configuration to allow instantiation from attributes
    """

    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class UsersPublic(BaseModel):
    """
    Represents a model for public user information.

    Attributes:
        data (Sequence[UserPublic]): A list of UserPublic objects.
        count (int): The total number of users.

    Example:
        users_public = UsersPublic(data=[user1, user2], count=2)

    Note:
        The configuration dict enables export of attributes from an instance.
    """

    data: Sequence[UserPublic]
    count: int

    model_config = ConfigDict(from_attributes=True)


class ForgotPassword(BaseModel):
    """
    This class represents a model for initiating a forgot password request.

    Attributes:
        email (EmailStr): The email address associated with the user account.

    Example usage:
        request = ForgotPassword(email="user@example.com")

    Error cases:
        - An invalid email address format will raise a validation error.
    """

    email: EmailStr


class NewPassword(BaseModel):
    """
    Data model representing new password reset request.

    Attributes:
        token (str): Unique token associated with the password reset request.
        new_password (str): New password to be set for the user.

    Example:
        new_password_request = NewPassword(token="abc123", new_password="newpassword123")
        # Use the new_password_request object to process a password reset in your application
    """

    token: str
    new_password: str


# Generic message
class Message(BaseModel):
    """
    This class represents a Message model, inheriting from BaseModel.

    Attributes:
        message (str): The textual content of the message.

    Example:
        >>> msg = Message(message="Hello, world!")
        >>> print(msg.message)
        Hello, world!

    Error Cases:
        - Ensure 'message' is passed as a string.
    """

    message: str
