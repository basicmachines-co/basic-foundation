import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from loguru import logger
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# get the current working directory
CWD = os.getcwd()
# print(f"CWD={CWD}")
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
logger.info(f"BASE_DIR={BASE_DIR}")

# find the .env in parent dirs
load_dotenv(verbose=True)


class Settings(BaseSettings):
    """

    This class represents the settings for the Basic API.

    Attributes:
        app_name (str): The name of the application.
        jwt_secret (str): The secret key for JSON Web Token (JWT) generation.
        postgres_user (str): The username for connecting to the PostgreSQL database.
        postgres_password (str): The password for connecting to the PostgreSQL database.
        postgres_db (str): The name of the PostgreSQL database.
        postgres_host (str): The host of the PostgreSQL database.
        postgres_port (int): The port of the PostgreSQL database.
        env_file (str): The path to the .env file (optional).

    Properties:
        postgres_dsn: Property that returns the PostgreSQL database connection URL.
    """

    API_V1_STR: str = "/api/v1"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    DOMAIN: str = "localhost"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    app_name: str = "Basic API"
    jwt_secret: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    env_file: str = None

    superuser_name: str
    superuser_email: str
    superuser_password: str

    EMAIL_SMTP_TLS: bool = True
    EMAIL_SMTP_SSL: bool = False
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_HOST: str | None = None
    EMAIL_SMTP_USER: str | None = None
    EMAIL_SMTP_PASSWORD: str | None = None
    EMAIL_FROM_EMAIL: str | None = None
    EMAIL_FROM_NAME: str | None = None
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def postgres_dsn_sync(self) -> PostgresDsn:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field  # type: ignore[misc]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.EMAIL_SMTP_HOST and self.EMAIL_FROM_EMAIL)

    # assume the .env file is in the directory above the project
    model_config = SettingsConfigDict(env_file=f"{CWD}/../.env", extra="allow")

    @computed_field  # type: ignore[misc]
    @property
    def server_host(self) -> str:
        # Use HTTPS for anything other than local development
        if self.ENVIRONMENT == "local":
            return f"http://{self.DOMAIN}"
        return f"https://{self.DOMAIN}"


# Note:
# * The `.env` file is assumed to be located in the directory above the project.
settings = Settings(env_file=f"{CWD}/../.env")
