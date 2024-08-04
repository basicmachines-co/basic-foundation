import uuid

import fastapi_users
from pydantic import BaseModel


class User(BaseModel):
    first_name: str
    last_name: str


class UserRead(User, fastapi_users.schemas.BaseUser[uuid.UUID]):
    pass


class UserCreate(User, fastapi_users.schemas.BaseUserCreate):
    pass


class UserUpdate(User, fastapi_users.schemas.BaseUserUpdate):
    pass
