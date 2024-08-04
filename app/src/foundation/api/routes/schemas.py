import uuid

from pydantic import BaseModel, EmailStr, ConfigDict


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
