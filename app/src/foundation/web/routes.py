from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi import Request, Form, Response, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import ValidationError
from starlette.responses import RedirectResponse, HTMLResponse

from app.core.config import BASE_DIR
from app.core.deps import get_user_repository
from app.core.repository import Repository
from app.fastapi_users.deps import (
    get_cookie_backend,
    fastapi_users,
    get_user_manager,
    current_optional_user,
)
from app.fastapi_users.managers import UserManager
from app.fastapi_users.models import User
from app.fastapi_users.schemas import UserCreate, UserUpdate


def logged_in(user: User = Depends(current_optional_user)):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={'Location': html_router.url_path_for("login")})
    return user


html_router = APIRouter(include_in_schema=False, default_response_class=HTMLResponse)

templates = Jinja2Blocks(
    directory=f"{BASE_DIR}/templates",
)
templates.env.add_extension(DebugExtension)


@html_router.get("/dashboard")
async def dashboard(request: Request, current_user=Depends(logged_in)):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "current_user": current_user},
    )


@html_router.get("/users")
async def users(
        request: Request,
        current_user=Depends(logged_in),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    users = await user_repo.find_all()
    return templates.TemplateResponse(
        "pages/user_list.html",
        {"request": request, "current_user": current_user, "users": users},
    )


@html_router.get("/users/{user_id}")
async def user(
        request: Request,
        user_id: UUID,
        current_user=Depends(logged_in),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    view_user = await user_repo.find_by_id(user_id)
    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "current_user": current_user, "user": view_user},
    )


@html_router.get("/users/{user_id}/edit")
async def user_edit(
        request: Request,
        user_id: UUID,
        current_user=Depends(logged_in),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    edit_user = await user_repo.find_by_id(user_id)
    return templates.TemplateResponse(
        "pages/user_edit.html",
        {"request": request, "current_user": current_user, "user": edit_user},
        block_name="content",
    )


@html_router.post("/users/{user_id}")
async def user_edit_post(
        request: Request,
        user_id: UUID,
        current_user=Depends(logged_in),
        first_name: str = Form(),
        last_name: str = Form(),
        email: str = Form(),
        is_active: str = Form(False),
        is_verified: str = Form(False),
        is_superuser: str = Form(False),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    user = await user_repo.find_by_id(user_id)
    # todo handle 404
    error = None
    try:
        update_form = UserUpdate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=is_active,
            is_verified=is_verified,
            is_superuser=is_superuser,
        )
    except ValidationError:
        error = "Validation Error"

    updated_user = await user_repo.update(user.id, update_form.dict())

    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "error": error, "user": updated_user},
        block_name="content",
    )


@html_router.get("/")
async def index(request: Request, current_user=Depends(logged_in)):
    return templates.TemplateResponse(
        "pages/index.html",
        {"request": request, "current_user": current_user},
    )


@html_router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(
        "pages/register.html", {"request": request}
    )


@html_router.post("/register")
async def register_post(
        request: Request,
        first_name: str = Form(),
        last_name: str = Form(),
        email: str = Form(),
        password: str = Form(),
        user_manager: UserManager = Depends(get_user_manager),
        auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    register_form = None
    try:
        register_form = UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
        )
        user = await user_manager.create(register_form, safe=True, request=request)
        return await login_user(request, user, user_manager, auth_backend)
    except ValidationError:
        error = "Validation Error"
    except exceptions.UserAlreadyExists:
        error = "User already exists"
    except exceptions.InvalidPasswordException as e:
        error = e.reason

    return templates.TemplateResponse(
        "pages/register.html",
        {"request": request, "error": error, **register_form.dict()},
        block_name="register_form",
    )


@html_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@html_router.post("/login")
async def login_post(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        user_manager: UserManager = Depends(get_user_manager),
        auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    user = await user_manager.authenticate(form_data)

    if user is None or not user.is_active:
        return templates.TemplateResponse(
            "pages/login.html",
            {
                "request": request,
                "error": "Incorrect Username or Password",
                "status_code": 401,
                "username": form_data.username,
            },
            block_name="login_form",
        )

    return await login_user(request, user, user_manager, auth_backend)


async def login_user(request, user, user_manager, auth_backend):
    strategy: Strategy[User, uuid.UUID] = auth_backend.get_strategy()
    login_response = await auth_backend.login(strategy, user)
    await user_manager.on_after_login(user, request, login_response)

    # redirect user to the dashboard
    login_response.headers["HX-Redirect"] = html_router.url_path_for("dashboard")
    return Response(headers=login_response.headers)


@html_router.get("/logout")
async def logout(
        request: Request,
        user_token=Depends(fastapi_users.authenticator.current_user_token(optional=True)),
        auth_backend: AuthenticationBackend = Depends(get_cookie_backend),
):
    # if the user is not logged in, redirect to index
    user, token = user_token
    if not user:
        response = RedirectResponse(url=html_router.url_path_for("index"))
        return response

    # clear cookie
    logout_response = await auth_backend.logout(
        auth_backend.get_strategy(), user, token
    )
    return RedirectResponse(
        url=html_router.url_path_for("index"), headers=logout_response.headers
    )
