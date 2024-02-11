import os
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from pydantic import PostgresDsn
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

    app_name: str = "Basic API"
    jwt_secret: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int
    env_file: str = None

    @property
    def postgres_dsn(self) -> PostgresDsn:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    # assume the .env file is in the directory above the project
    model_config = SettingsConfigDict(env_file=f"{CWD}/../.env", extra="allow")


# Note:
# * The `.env` file is assumed to be located in the directory above the project.
settings = Settings(env_file=f"{CWD}/../.env")
