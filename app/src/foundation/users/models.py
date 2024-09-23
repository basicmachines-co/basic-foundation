from typing import Optional
from uuid import UUID

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column

from foundation.core.models import BaseWithId


class User(BaseWithId):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=func.gen_random_uuid()
    )
    full_name: Mapped[Optional[str]]
    email: Mapped[str] = mapped_column(String())
    hashed_password: Mapped[str] = mapped_column(String())
    is_active: Mapped[Optional[bool]] = mapped_column(nullable=False, default=False)
    is_superuser: Mapped[Optional[bool]] = mapped_column(nullable=False, default=False)
