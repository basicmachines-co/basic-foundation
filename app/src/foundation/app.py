import logging
import sys

from fastapi import FastAPI
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_wtf import CSRFProtectMiddleware

import tools.init_data
from foundation.api.routes.auth import router as api_auth_router
from foundation.api.routes.users import router as api_user_router
from foundation.core import config
from foundation.core.config import BASE_DIR, settings
from foundation.web.routes.app import router as html_app_router
from foundation.web.routes.auth import router as html_auth_router
from foundation.web.routes.users import router as html_users_router
from foundation.web.templates import templates

# delete all existing default loggers
logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)

app = FastAPI()

# Add middleware for sessions and CSRF protection
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)
app.add_middleware(CSRFProtectMiddleware, csrf_secret=settings.CSRF_SECRET)

app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")

# api routes
app.include_router(api_auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(api_user_router, prefix="/api/users", tags=["users"])

# web html routes
app.include_router(html_users_router)
app.include_router(html_app_router)
app.include_router(html_auth_router)


@app.on_event("startup")
async def on_startup():
    """
    Set up tasks to be executed on application startup.

    :return: None
    """
    logger.info(f"Welcome to {config.settings.app_name}")

    # silence bcrypt noise
    logging.getLogger("passlib").setLevel(logging.ERROR)

    # setup admin user if not present in db
    tools.init_data.main()


from fastapi.exception_handlers import (
    http_exception_handler,
)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    accept_header = request.headers.get("accept", "")

    if "text/html" in accept_header:
        if exc.status_code == 403:
            return templates.TemplateResponse(
                "pages/403.html", {"request": request}, status_code=403
            )
        elif exc.status_code == 404:
            return templates.TemplateResponse(
                "pages/404.html", {"request": request}, status_code=404
            )
        elif exc.status_code == 500:
            return templates.TemplateResponse(
                "pages/500.html", {"request": request}, status_code=500
            )

    return await http_exception_handler(request, exc)
