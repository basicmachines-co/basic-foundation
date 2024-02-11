import sys

from fastapi import FastAPI
from loguru import logger
from starlette.staticfiles import StaticFiles

from basic_api import config
from basic_api.config import BASE_DIR
from basic_api.routes import html_router
from basic_api.users.routes import auth_router, user_router

# delete all existing default loggers
logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(html_router, tags=["html"])


@app.on_event("startup")
async def on_startup():
    # Not needed if you set up a migration system like Alembic
    logger.info(f"Welcome to {config.settings.app_name}")
