import logging
import sys

from fastapi import FastAPI
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette_wtf import CSRFProtectMiddleware

from foundation.tools import init_data
from foundation.core import config
from foundation.core.config import BASE_DIR, settings
from modules.foundation.web.templates import templates

from modules.foundation.api.routes import api_router  # Import the router from api module
from modules.foundation.web.routes import html_router  # Import the router from web module
from fastapi.exception_handlers import (
    http_exception_handler,
)

# delete all existing default loggers
logger.remove()
logger.add(sys.stderr, colorize=True, backtrace=True, diagnose=True)

app = FastAPI(title=settings.APP_NAME)

# Add middleware for sessions and CSRF protection
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)
app.add_middleware(CSRFProtectMiddleware, csrf_secret=settings.CSRF_SECRET)

app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/modules/foundation/web/static"), name="static")

# include routes from modules
app.include_router(api_router, prefix="/api")
app.include_router(html_router)


@app.on_event("startup")
async def on_startup():  # pragma: no cover
    """
    Set up tasks to be executed on application startup.

    :return: None
    """
    logger.info(f"Welcome to {config.settings.APP_NAME}")

    # silence bcrypt noise
    logging.getLogger("passlib").setLevel(logging.ERROR)

    # setup admin user if not present in db
    init_data.main()




@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc): #pragma: no cover
    accept_header = request.headers.get("accept", "")

    if "text/html" in accept_header:  # pragma: no cover
        if exc.status_code == 403:
            return templates.TemplateResponse(
                "pages/403.html", {"request": request}, status_code=403
            )
        elif exc.status_code == 404:
            return templates.TemplateResponse(
                "pages/404.html", {"request": request}, status_code=404
            )
        elif exc.status_code == 500:  # pragma: no cover
            return templates.TemplateResponse(
                "pages/500.html", {"request": request}, status_code=500
            )

    return await http_exception_handler(request, exc)
