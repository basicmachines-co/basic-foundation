import uuid

from fastapi import Depends, Request, Form, Response, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_users import exceptions
from fastapi_users.authentication import AuthenticationBackend, Strategy
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic.error_wrappers import ValidationError
from starlette.responses import RedirectResponse, HTMLResponse

from basic_api.config import BASE_DIR
from basic_api.users.deps import (
    get_cookie_backend,
    fastapi_users,
    get_user_manager,
    current_optional_user,
)
from basic_api.users.managers import UserManager
from basic_api.users.models import User
from basic_api.users.schemas import UserCreate

html_router = APIRouter(
    tags=["html"],
)

templates = Jinja2Blocks(
    directory=f"{BASE_DIR}/templates",
)
templates.env.add_extension(DebugExtension)


@html_router.get("/", response_class=HTMLResponse)
async def index(request: Request, user=Depends(current_optional_user)):
    if not user:
        return RedirectResponse(url=html_router.url_path_for("login"))
    return templates.TemplateResponse(
        "pages/index.html.jinja",
        {"request": request, "title": "Basic Foundation", "user": user},
    )


@html_router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        "pages/register.html.jinja", {"request": request, "title": "Register"}
    )


@html_router.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    user_manager: UserManager = Depends(get_user_manager),
):
    errors = []
    register_form = None
    try:
        register_form = UserCreate(email=email, password=password)
        await user_manager.create(register_form, safe=True, request=request)
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


@html_router.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("pages/login.html.jinja", {"request": request})


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

    login_response.headers["HX-Redirect"] = html_router.url_path_for("index")
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
