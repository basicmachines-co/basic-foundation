import os
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from loguru import logger
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# get the current working directory
CWD = os.getcwd()
# print(f"CWD={CWD}")
BASE_DIR = Path(__file__).resolve().parent.parent.parent
logger.info(f"BASE_DIR={BASE_DIR}")

# find the .env in parent dirs
load_dotenv(verbose=True)


class Settings(BaseSettings):
    """
    Settings configuration class that holds various application settings.

    Attributes:
        env_file (str): Path to the environment file.

        API_URL (str): URL of the API.
        APP_NAME (str): Name of the application.

        ACCESS_TOKEN_EXPIRE_MINUTES (int): Token expiration time in minutes. Default is 60 * 24 * 8.
        DOMAIN (str): Domain name. Default is "localhost".
        ENVIRONMENT (Literal): Environment type; can be "local", "ci", or "production". Default is "local".

        JWT_SECRET (str): Secret key for JWT.
        CSRF_SECRET (str): Secret key for CSRF.

        DATABASE_URL (str | None): Database URL; either this has to be set or each individual PostgreSQL value.
        POSTGRES_USER (str | None): PostgreSQL user.
        POSTGRES_PASSWORD (str | None): PostgreSQL password.
        POSTGRES_DB (str | None): PostgreSQL database name.
        POSTGRES_HOST (str | None): PostgreSQL host.
        POSTGRES_PORT (int | None): PostgreSQL port.

        SUPERUSER_NAME (str): Superuser name.
        SUPERUSER_EMAIL (str): Superuser email.
        SUPERUSER_PASSWORD (str): Superuser password.

        EMAIL_ENABLED (bool): Email service enabled flag. Default is True.
        EMAIL_SMTP_TLS (bool): Use TLS for SMTP. Default is True.
        EMAIL_SMTP_SSL (bool): Use SSL for SMTP. Default is False.
        EMAIL_SMTP_PORT (int): SMTP port. Default is 587.
        EMAIL_SMTP_HOST (str | None): SMTP host.
        EMAIL_SMTP_USER (str | None): SMTP user.
        EMAIL_SMTP_PASSWORD (str | None): SMTP password.
        EMAIL_FROM_EMAIL (str | None): From email address.
        EMAIL_FROM_NAME (str | None): From name.
        EMAIL_RESET_TOKEN_EXPIRE_HOURS (int): Reset token expiration time in hours. Default is 48.

    Methods:
        postgres_url(self, *, is_async: bool = True) -> str:
            Constructs a PostgreSQL URL based on the settings.
            Param is_async: Boolean flag to indicate if the URL should be asynchronous.

        postgres_dsn(self) -> str:
            Property that returns the PostgreSQL DSN for asynchronous connections. Falls back to constructing the URL if DATABASE_URL is not set.

        postgres_dsn_sync(self) -> str:
            Property that returns the PostgreSQL DSN for synchronous connections.

        server_host(self) -> str:
            Property that returns the server host URL. Uses HTTPS for environments other than local development.
    """

    env_file: str

    API_URL: str
    APP_NAME: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "ci", "production"] = "local"

    JWT_SECRET: str
    CSRF_SECRET: str

    # either DATABASE_URL has to be set
    DATABASE_URL: str | None = None
    # or each POSTGRES VALUE
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int | None = None

    SUPERUSER_NAME: str
    SUPERUSER_EMAIL: str
    SUPERUSER_PASSWORD: str

    EMAIL_ENABLED: bool = True
    EMAIL_SMTP_TLS: bool = True
    EMAIL_SMTP_SSL: bool = False
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_HOST: str | None = None
    EMAIL_SMTP_USER: str | None = None
    EMAIL_SMTP_PASSWORD: str | None = None
    EMAIL_FROM_EMAIL: str | None = None
    EMAIL_FROM_NAME: str | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    def postgres_url(self, *, is_async: bool = True) -> str:
        asyncpg = "+asyncpg" if is_async else ""
        return f"postgresql{asyncpg}://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def postgres_dsn(self) -> str:  # pragma: no cover
        if not self.DATABASE_URL:
            return self.postgres_url(is_async=True)
        # the render DATEBASE_URL is in the non async format
        return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def postgres_dsn_sync(self) -> str:  # pragma: no cover
        return self.DATABASE_URL or self.postgres_url(is_async=False)

    # assume the .env file is in the directory above the project
    model_config = SettingsConfigDict(env_file=f"{CWD}/../.env", extra="allow")

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:  # pragma: no cover
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}:8000"
        return f"https://{self.DOMAIN}"


# Note:
# * The `.env` file is assumed to be located in the directory above the project.
settings = Settings(env_file=f"{CWD}/../.env")  # pyright: ignore [reportCallIssue]
