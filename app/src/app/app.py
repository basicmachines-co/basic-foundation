import sys

from fastapi import FastAPI
from loguru import logger
from starlette.staticfiles import StaticFiles

from app import config
from app.api.routes.auth import router as login_api_router
from app.api.routes.users import router as user_api_router
from app.config import BASE_DIR
from app.fastapi_users.routes import auth_router, user_router
from app.web.routes import html_router

# delete all existing default loggers
logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

app.include_router(login_api_router, prefix="")
app.include_router(user_api_router, prefix="/users")
app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(html_router, tags=["html"])


@app.on_event("startup")
async def on_startup():
    """
    Set up tasks to be executed on application startup.

    :return: None
    """
    # Not needed if you set up a migration system like Alembic
    logger.info(f"Welcome to {config.settings.app_name}")
