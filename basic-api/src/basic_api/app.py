import os
import uuid

from fastapi import Depends, FastAPI, Request, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from pydantic.error_wrappers import ValidationError
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
    get_cookie_backend,
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
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
        "register-form.html", {"request": request, "errors": errors}
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
    auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    user = await user_manager.authenticate(form_data)

    if user is None or not user.is_active:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "detail": "Incorrect Username or Password",
                "status_code": 401,
            },
        )

    strategy: Strategy[User, uuid.UUID] = auth_backend.get_strategy()
    login_response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, login_response)

    return templates.TemplateResponse(
        "success.html",
        {
            "request": request,
            "USERNAME": user.email,
            "success_msg": "Welcome back! ",
            "path_route": "/private/",
            "path_msg": "Go to your private page!",
        },
        headers=login_response.headers,
    )


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}


@app.get("/private/", response_class=HTMLResponse)
async def private(request: Request, user: User = Depends(current_active_user)):
    try:
        return templates.TemplateResponse("private.html", {"request": request})
    except:
        raise Exception()


@app.on_event("startup")
async def on_startup():
    # Not needed if you set up a migration system like Alembic
    await create_db_and_tables()
