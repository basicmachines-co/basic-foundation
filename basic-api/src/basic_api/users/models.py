from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID

from basic_api.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
