import logging
import sys

import typer
from loguru import logger
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from foundation.core.config import settings
from foundation.core.security import get_password_hash
from foundation.core.users.models import User, StatusEnum, RoleEnum

# silence bcrypt noise
logging.getLogger("passlib").setLevel(logging.ERROR)

logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)


def main():  # pragma: no cover
    """
    Creates a default admin user if it does not already exist. Uses settings
    for defining admin user's properties like name, email, status, role, and
    hashed password. Checks for user existence in a PostgreSQL database using
    the provided Data Source Name (DSN). If user is already present, logs
    that information. If not, creates the user and logs the information.

    :raises Exception: If there is an error during the user creation process

    Example:
        main()
    """
    user = User(
        full_name=settings.SUPERUSER_NAME,
        email=settings.SUPERUSER_EMAIL,
        status=StatusEnum.ACTIVE,
        role=RoleEnum.ADMIN,
        hashed_password=get_password_hash(settings.SUPERUSER_PASSWORD),
    )

    engine = create_engine(settings.postgres_dsn_sync)
    with Session(engine) as session:
        statement = select(User).where(User.email == settings.SUPERUSER_EMAIL)
        admin_user = session.scalars(statement).one_or_none()
        if admin_user is None:
            logger.info(
                f"Creating default admin user name: {settings.SUPERUSER_NAME}, email {settings.SUPERUSER_EMAIL}"
            )
            try:
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(
                    f"successfully created default admin user with id {user.id}"
                )
            except Exception as e:
                logger.error(e)
        else:
            logger.info(
                f"Found admin user name: {settings.SUPERUSER_NAME}, email: {settings.SUPERUSER_EMAIL}"
            )


if __name__ == "__main__":  # pragma: no cover
    typer.run(main)
