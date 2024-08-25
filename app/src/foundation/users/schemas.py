import re
import uuid

from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthTokenPayload(BaseModel):
    id: uuid.UUID


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = False
    is_superuser: bool = False
    full_name: str | None


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, value):
        # Ensure password is at least 8 characters long
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long.')

        # Ensure password has at least one uppercase letter
        if not re.search(r'[A-Z]', value):
            raise ValueError('Password must contain at least one uppercase letter.')

        # Ensure password has at least one lowercase letter
        if not re.search(r'[a-z]', value):
            raise ValueError('Password must contain at least one lowercase letter.')

        # Ensure password has at least one digit
        if not re.search(r'\d', value):
            raise ValueError('Password must contain at least one digit.')

        # Ensure password has at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValueError('Password must contain at least one special character.')

        return value


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None


class UserUpdate(UserBase):
    email: EmailStr | None
    password: str | None


class UserUpdateMe(BaseModel):
    full_name: str | None
    email: EmailStr | None


class UpdatePassword(BaseModel):
    current_password: str
    new_password: str


class UserPublic(UserBase):
    id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)


class UsersPublic(BaseModel):
    data: list[UserPublic]
    count: int

    model_config = ConfigDict(from_attributes=True)


class ForgotPassword(BaseModel):
    email: EmailStr


class NewPassword(BaseModel):
    token: str
    new_password: str


# Generic message
class Message(BaseModel):
    message: str
