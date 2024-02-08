from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from basic_api.config import CWD
from basic_api.db import create_db_and_tables
from basic_api.routes import html_router
from basic_api.users.routes import auth_router, user_router

app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{CWD}/static"), name="static")

app.include_router(auth_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(html_router, tags=["html"])


@app.on_event("startup")
async def on_startup():
    # Not needed if you set up a migration system like Alembic
    await create_db_and_tables()
