from fastapi_users.db import SQLAlchemyBaseUserTableUUID

from basic_api.db import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass
