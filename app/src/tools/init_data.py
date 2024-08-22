import logging
import sys

import typer
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from foundation.core.config import settings
from foundation.core.security import get_password_hash
from foundation.users.models import User

# silence bcrypt noise
logging.getLogger('passlib').setLevel(logging.ERROR)

logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)


def main():
    user = User(full_name=settings.SUPERUSER_NAME, email=settings.SUPERUSER_EMAIL, is_active=True, is_superuser=True,
                hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD))

    engine = create_engine(settings.postgres_dsn_sync)
    with Session(engine) as session:

        statement = select(User).where(settings.SUPERUSER_EMAIL == User.email)
        admin_user = session.scalars(statement).one_or_none()
        if admin_user is None:
            logger.info(
                f"Creating default admin user name: {settings.SUPERUSER_NAME}, email {settings.SUPERUSER_EMAIL}")
            try:
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"successfully created default admin user with id {user.id}")
            except Exception as e:
                logger.error(e)
        else:
            logger.info(f"Found admin user name: {settings.SUPERUSER_NAME}, email: {settings.SUPERUSER_EMAIL}")


if __name__ == "__main__":
    typer.run(main)
