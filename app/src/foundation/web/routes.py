from datetime import timedelta
from uuid import UUID

from fastapi import Depends, status
from fastapi import Request, Form, Response, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from jinja2.ext import DebugExtension
from jinja2_fragments.fastapi import Jinja2Blocks
from pydantic import ValidationError
from sqlalchemy import select
from starlette.responses import RedirectResponse, HTMLResponse

from foundation.core.config import BASE_DIR, settings
from foundation.core.security import verify_password_reset_token
from foundation.users.deps import UserServiceDep, UserPaginationDep
from foundation.users.models import User
from foundation.users.schemas import AuthTokenPayload, UserCreate
from foundation.users.services import UserCreateError, UserValueError, UserNotFoundError
from foundation.web.deps import CurrentUserDep, access_token_security

html_router = APIRouter(include_in_schema=False, default_response_class=HTMLResponse)

templates = Jinja2Blocks(
    directory=f"{BASE_DIR}/templates",
)
templates.env.add_extension(DebugExtension)


@html_router.get("/dashboard")
async def dashboard(request: Request, user_service: UserServiceDep, current_user: CurrentUserDep):
    users_count = await user_service.get_users_count()
    active_users_count = await user_service.get_active_users_count()
    admin_users_count = await user_service.get_admin_users_count()

    return templates.TemplateResponse(
        "pages/dashboard.html",
        {
            "request": request,
            "users_count": users_count,
            "active_users_count": active_users_count,
            "admin_users_count": admin_users_count,
        },
    )


@html_router.get("/users")
async def users(
        request: Request,
        user_pagination: UserPaginationDep,
        current_user: CurrentUserDep,
        page: int = 1,
        page_size: int = 10,
):
    query = select(User)
    pagination = user_pagination.paginate(query, page_size=page_size)
    page = await pagination.page(page=page)

    return templates.TemplateResponse(
        "pages/user_list.html",
        {
            "request": request,
            "page": page

        },
    )


@html_router.get("/users/create")
async def user_create(
        request: Request,
        current_user: CurrentUserDep,
):
    return templates.TemplateResponse(
        "pages/user_create.html",
        {"request": request, "current_user": current_user, "user": None},
    )


@html_router.post("/users/create")
async def user_create_post(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
        full_name: str = Form(),
        email: str = Form(),
        password: str = Form(),
        is_active: bool = Form(False),
        is_superuser: bool = Form(False),
):
    error = None
    try:
        created_user = await user_service.create_user(create_dict={"full_name": full_name,
                                                                   "email": email,
                                                                   "password": password,
                                                                   "is_active": is_active,
                                                                   "is_superuser": is_superuser})
    except UserValueError as e:
        error = e.args
        return templates.TemplateResponse(
            "pages/user_create.html",
            {"request": request, "error": error, "user": {"full_name": full_name,
                                                          "email": email,
                                                          "is_active": is_active,
                                                          "is_superuser": is_superuser}},
            block_name="content",
        )

    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "error": error, "user": created_user},
        block_name="content",
    )


@html_router.get("/users/{user_id}")
async def user(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    view_user = await user_service.get_user_by_id(user_id=user_id)
    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "current_user": current_user, "user": view_user},
    )


@html_router.get("/users/{user_id}/edit")
async def user_edit(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    edit_user = await user_service.get_user_by_id(user_id=user_id)
    return templates.TemplateResponse(
        "pages/user_edit.html",
        {"request": request, "current_user": current_user, "user": edit_user},
        block_name="content",
    )


@html_router.post("/users/{user_id}")
async def user_edit_post(
        request: Request,
        user_id: UUID,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
        full_name: str = Form(),
        email: str = Form(),
        is_active: bool = Form(False),
        is_superuser: bool = Form(False),
):
    error = None
    try:
        updated_user = await user_service.update_user(user_id=user_id, update_dict={"full_name": full_name,
                                                                                    "email": email,
                                                                                    "is_active": is_active,
                                                                                    "is_superuser": is_superuser})
    except UserValueError as e:
        error = e.args
        return templates.TemplateResponse(
            "pages/user_edit.html",
            {"request": request, "error": error, "user": {"full_name": full_name,
                                                          "email": email,
                                                          "is_active": is_active,
                                                          "is_superuser": is_superuser}},
            block_name="content",
        )

    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "error": error, "user": updated_user},
        block_name="content",
    )


@html_router.get("/")
async def index(request: Request, current_user: CurrentUserDep):
    if not current_user:
        return RedirectResponse(url=html_router.url_path_for("login"))

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
        user_service: UserServiceDep,
        full_name: str = Form(),
        email: str = Form(),
        password: str = Form(),
):
    register_form = None
    try:
        register_form = UserCreate(
            full_name=full_name,
            email=email,
            password=password,
            is_active=True
        )
        user = await user_service.create_user(create_dict=register_form.model_dump())
        return await login_user(user)
    except ValidationError:
        error = "Validation Error"
    except UserCreateError:
        error = "User already exists"

    return templates.TemplateResponse(
        "pages/register.html",
        {"request": request, "error": error, **register_form.model_dump()},
        block_name="register_form",
    )


@html_router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@html_router.post("/login")
async def login_post(
        request: Request,
        user_service: UserServiceDep,
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await user_service.authenticate(
        email=form_data.username, password=form_data.password
    )

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

    return await login_user(user)


async def login_user(user: User):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = access_token_security.create_access_token(subject=jsonable_encoder(AuthTokenPayload(id=user.id)),
                                                      expires_delta=access_token_expires)
    access_token_security.set_access_cookie(response, token, access_token_expires)
    # redirect user to the dashboard
    response.headers["HX-Redirect"] = html_router.url_path_for("dashboard")
    return Response(headers=response.headers)


@html_router.get("/logout")
async def logout():
    # clear cookie
    response = RedirectResponse(url=html_router.url_path_for("index"))
    access_token_security.unset_access_cookie(response)
    return response


@html_router.get("/forgot-password")
async def forgot_password(request: Request):
    return templates.TemplateResponse("pages/forgot_password.html", {"request": request})


@html_router.post("/forgot-password")
async def forgot_password_post(request: Request, user_service: UserServiceDep, email: str = Form()):
    error = None
    success = None
    try:
        await user_service.recover_password(email=email)
        success = f"An email was sent to {email}"
    except UserNotFoundError as e:
        error = e.args[0]
    return templates.TemplateResponse("pages/forgot_password.html",
                                      {"request": request, "error": error,
                                       "success": success},
                                      block_name="forgot_password_form")


@html_router.get("/reset-password")
async def reset_password(request: Request, token: str):
    context = {"request": request}
    email = verify_password_reset_token(token=token)
    if not email:
        context["error"] = "Invalid token"

    context["token"] = token
    return templates.TemplateResponse("pages/reset_password.html", context)


@html_router.post("/reset-password")
async def reset_password_post(request: Request, user_service: UserServiceDep, token: str = Form(),
                              new_password: str = Form()):
    context = {"request": request}
    email = verify_password_reset_token(token=token)
    if not email:
        context["error"] = "Invalid token"

    try:
        user = await user_service.get_user_by_email(email=email)
        updated_user = await user_service.update_user(user_id=user.id, update_dict={
            "password": new_password,
        })
        context["success"] = "Your password has been updated!"
    except UserNotFoundError as e:
        context["error"] = e.args[0]

    if not user.is_active:
        context["error"] = "Your account is not active, please check your email"

    context["token"] = token
    return templates.TemplateResponse("pages/reset_password.html", context, block_name="password_reset_form")


@html_router.get("/profile")
async def profile(
        request: Request,
        user_service: UserServiceDep,
        current_user: CurrentUserDep,
):
    view_user = await user_service.get_user_by_id(user_id=current_user.id)
    return templates.TemplateResponse(
        "pages/user_view.html",
        {"request": request, "current_user": current_user, "user": view_user},
    )
