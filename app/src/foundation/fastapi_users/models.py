from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import mapped_column

from foundation.core.models import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    first_name = mapped_column(String)
    last_name = mapped_column(String)
