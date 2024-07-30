import uuid

from pydantic import BaseModel


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthTokenPayload(BaseModel):
    id: uuid.UUID
