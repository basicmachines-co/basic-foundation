import os
from pathlib import Path
from typing import Literal

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
    This class represents the settings for the Basic API.
    """

    API_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    app_name: str = "Basic API"
    JWT_SECRET: str
    CSRF_SECRET: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    env_file: str

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
    def postgres_dsn(self) -> str:
        return self.postgres_url(is_async=True)

    @property
    def postgres_dsn_sync(self) -> str:  # pragma: no cover
        return self.postgres_url(is_async=False)

    @computed_field  # type: ignore[misc]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.EMAIL_SMTP_HOST and self.EMAIL_FROM_EMAIL)

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
