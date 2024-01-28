import os
import uuid

from fastapi import Depends, FastAPI, Request, Form, responses, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from fastapi_users.router import ErrorCode
from pydantic.error_wrappers import ValidationError
from starlette import status
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles

from basic_api.db import User, create_db_and_tables
from basic_api.schemas import UserCreate, UserRead, UserUpdate
from basic_api.users import (
    jwt_backend,
    current_active_user,
    fastapi_users,
    get_user_manager,
    UserManager,
    cookie_backend,
)

CWD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{CWD}/static"), name="static")
templates = Jinja2Templates(directory=f"{CWD}/templates")

app.include_router(
    fastapi_users.get_auth_router(jwt_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/")
def read_root():
    return {"Hello": "World!"}


@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    return templates.TemplateResponse(
        request=request, name="item.html", context={"id": id}
    )


@app.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
async def register(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    user_manager: UserManager = Depends(get_user_manager),
):
    errors = []
    try:
        user = await user_manager.create(
            UserCreate(email=email, password=password), safe=True, request=request
        )
        return responses.RedirectResponse(
            "/?alert=Successfully%20Registered", status_code=status.HTTP_302_FOUND
        )
    except (
        ValidationError,
        exceptions.UserAlreadyExists,
        exceptions.InvalidPasswordException,
    ) as e:
        errors.append(e)
        return templates.TemplateResponse(
            "register.html", {"request": request, "errors": errors}
        )


@app.get("/login")
def register(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post(
    "/login",
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
    auth_backend: AuthenticationBackend = Depends(cookie_backend),
):
    user = await user_manager.authenticate(form_data)

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
        )

    strategy: Strategy[User, uuid.UUID] = auth_backend.get_strategy()
    login_response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, login_response)
    url = app.url_path_for("authenticated_route")
    return responses.RedirectResponse(
        url=url, headers=login_response.headers, status_code=status.HTTP_302_FOUND
    )


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.on_event("startup")
async def on_startup():
    # Not needed if you set up a migration system like Alembic
    await create_db_and_tables()
