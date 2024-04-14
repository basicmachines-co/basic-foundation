from typing import Callable, Coroutine, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi import Request, Form, Response, APIRouter
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import ValidationError
from starlette.responses import RedirectResponse, HTMLResponse

from api.config import BASE_DIR
from api.deps import get_user_repository
from api.repository import Repository
from api.users.deps import (
    get_cookie_backend,
    fastapi_users,
    get_user_manager,
    current_optional_user,
    current_active_user,
)
from api.users.managers import UserManager
from api.users.models import User
from api.users.schemas import UserCreate


class HTMLRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def login_redirect_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except HTTPException as exc:
                if exc.status_code == status.HTTP_401_UNAUTHORIZED:
                    response = RedirectResponse(url=html_router.url_path_for("login"))
                    return response

        return login_redirect_handler


html_router = APIRouter(tags=["html"], route_class=HTMLRoute)

templates = Jinja2Blocks(
    directory=f"{BASE_DIR}/templates",
)
templates.env.add_extension(DebugExtension)


@html_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user=Depends(current_active_user)):
    return templates.TemplateResponse(
        "pages/dashboard.html",
        {"request": request, "params": {"nav": "dashboard"}},
    )


@html_router.get("/users", response_class=HTMLResponse)
async def users(
        request: Request,
        current_user=Depends(current_active_user),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    users = await user_repo.find_all()
    return templates.TemplateResponse(
        "pages/user_list.html",
        {"request": request, "users": users},
    )


@html_router.get("/users/{id}", response_class=HTMLResponse)
async def user(request: Request, current_active_user=Depends(current_active_user)):
    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "params": {"nav": "users"}},
    )


@html_router.get("/users/{user_id}/edit", response_class=HTMLResponse)
async def user_edit(
        request: Request,
        user_id: UUID,
        current_active_user=Depends(current_active_user),
        user_repo: Repository[User] = Depends(get_user_repository),
):
    user = await user_repo.find_by_id(user_id)
    return templates.TemplateResponse(
        "pages/user_edit.html",
        {"request": request, "user": user},
        # block_name="content",
    )


@html_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(current_optional_user)):
    """
    :param request: Request object representing the HTTP request.
    :param user: Optional user object representing the current user.
    :return: A TemplateResponse object representing the HTML response.

    The index function handles the root route ("/"). It expects a Request object and an optional user object as
    parameters. If the user object is not provided, the function redirects the * user to the login page. Otherwise,
    it returns a TemplateResponse object that renders the "pages/index.html.jinja" template. The TemplateResponse
    object includes the request object *, the title "Basic Foundation", and the user object as template variables.
    """
    if not user:
        return RedirectResponse(url=html_router.url_path_for("login"))
    return templates.TemplateResponse(
        "pages/index.html",
        {"request": request, "title": "Basic Foundation", "user": user},
    )


@html_router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    """
    Register Method

    This method is used to handle the GET request for the "/register" route.
    It returns a template response for the registration page.

    :param request: The request object representing the HTTP request.
    :return: The template response object for the registration page.
    """
    return templates.TemplateResponse(
        "pages/register.html", {"request": request, "title": "Register"}
    )


@html_router.post("/register", response_class=HTMLResponse)
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


@html_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@html_router.post("/login", response_class=HTMLResponse)
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


@html_router.get("/logout", response_class=HTMLResponse)
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
