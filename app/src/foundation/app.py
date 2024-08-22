import logging
import sys

from fastapi import FastAPI
from loguru import logger
from starlette.staticfiles import StaticFiles

import tools.init_data
from foundation.api.routes.auth import router as api_auth_router
from foundation.api.routes.users import router as api_user_router
from foundation.core import config
from foundation.core.config import BASE_DIR
from foundation.web.routes import html_router

# delete all existing default loggers
logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

app.include_router(api_auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(api_user_router, prefix="/api/users", tags=["users"])
app.include_router(html_router, tags=["html"])


@app.on_event("startup")
async def on_startup():
    """
    Set up tasks to be executed on application startup.

    :return: None
    """
    logger.info(f"Welcome to {config.settings.app_name}")

    # silence bcrypt noise
    logging.getLogger('passlib').setLevel(logging.ERROR)

    # setup admin user if not present in db
    tools.init_data.main()
