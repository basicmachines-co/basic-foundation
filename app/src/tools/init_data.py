import logging
import sys

import typer
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.users.models import User

# silence bcrypt noise
logging.getLogger('passlib').setLevel(logging.ERROR)

logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)


def main():
    logger.info(f"Creating default admin user {settings.superuser_name}")
    user = User(full_name=settings.superuser_name, email=settings.superuser_email, is_active=True, is_superuser=True,
                hashed_password=get_password_hash(settings.superuser_password))

    engine = create_engine(settings.postgres_dsn_sync)
    with Session(engine) as session:

        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"successfully created default admin user with id {user.id}")
        except Exception as e:
            logger.error(e)


if __name__ == "__main__":
    typer.run(main)
