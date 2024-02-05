import os
import uuid

from fastapi import Depends, FastAPI, Request, Form, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic.error_wrappers import ValidationError
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from basic_api.db import User, create_db_and_tables
from basic_api.schemas import UserCreate, UserRead, UserUpdate
from basic_api.users import (
    jwt_backend,
    fastapi_users,
    get_user_manager,
    UserManager,
    get_cookie_backend,
    current_optional_user,
)

CWD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
app = FastAPI()

app.mount("/static", StaticFiles(directory=f"{CWD}/static"), name="static")
templates = Jinja2Blocks(
    directory=f"{CWD}/templates",
)
templates.env.add_extension(DebugExtension)

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
async def index(request: Request, user=Depends(current_optional_user)):
    if not user:
        return RedirectResponse(url=app.url_path_for("login"))

    return templates.TemplateResponse(
        "pages/index.html.jinja",
        {"request": request, "title": "Basic Foundation", "user": user.email},
    )


@app.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(
        "pages/register.html.jinja", {"request": request, "title": "Register"}
    )


@app.post("/register")
async def register(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    user_manager: UserManager = Depends(get_user_manager),
):
    errors = []
    register_form = None
    try:
        register_form = UserCreate(email=email, password=password)
        user = await user_manager.create(register_form, safe=True, request=request)
        return templates.TemplateResponse(
            "success.html",
            {
                "request": request,
                "success_msg": "Registration Successful!",
                "path_route": "/",
                "path_msg": "Click here to login!",
            },
        )
    except ValidationError:
        errors.append("Validation Error")
    except exceptions.UserAlreadyExists:
        errors.append("User already exists")
    except exceptions.InvalidPasswordException as e:
        errors.append(e.reason)

    return templates.TemplateResponse(
        "pages/register.html.jinja",
        {"request": request, "errors": errors, "email": register_form.email},
        block_name="register_form",
    )


@app.get("/login")
async def register(request: Request):
    return templates.TemplateResponse("pages/login.html.jinja", {"request": request})


@app.post(
    "/login",
)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_manager: UserManager = Depends(get_user_manager),
    auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    user = await user_manager.authenticate(form_data)

    if user is None or not user.is_active:
        return templates.TemplateResponse(
            "pages/login.html.jinja",
            {
                "request": request,
                "error": "Incorrect Username or Password",
                "status_code": 401,
                "username": form_data.username,
            },
            block_name="login_form",
        )

    strategy: Strategy[User, uuid.UUID] = auth_backend.get_strategy()
    login_response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, login_response)

    login_response.headers["HX-Redirect"] = app.url_path_for("index")
    return Response(headers=login_response.headers)


@app.get("/logout")
async def logout(
    request: Request,
    user_token=Depends(fastapi_users.authenticator.current_user_token(optional=True)),
    auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    # if the user is not logged in, redirect to index
    user, token = user_token
    if not user:
        response = RedirectResponse(url=app.url_path_for("index"))
        return response

    # clear cookie
    logout_response = await auth_backend.logout(
        auth_backend.get_strategy(), user, token
    )
    return RedirectResponse(
        url=app.url_path_for("index"), headers=logout_response.headers
    )


@app.on_event("startup")
async def on_startup():
    # Not needed if you set up a migration system like Alembic
    await create_db_and_tables()
