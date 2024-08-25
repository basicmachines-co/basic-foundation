from datetime import timedelta

from fastapi import Depends, status
from fastapi import Request, Form, Response
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from starlette.responses import RedirectResponse

from foundation.core.config import settings
from foundation.core.security import verify_password_reset_token
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.schemas import AuthTokenPayload, UserCreate
from foundation.users.services import UserCreateError, UserNotFoundError
from foundation.web.deps import access_token_security
from foundation.web.templates import templates
from foundation.web.utils import HTMLRouter

router = HTMLRouter()


@router.get("/register")
async def register(request: Request):
    return templates.TemplateResponse(
        "pages/register.html",
        dict(request=request, errors={})
    )


@router.post("/register")
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
            full_name=full_name, email=email, password=password, is_active=True
        )
        user = await user_service.create_user(create_dict=register_form.model_dump())
        return await login_user(request, user)
    except UserCreateError:
        error = "User already exists"

    return templates.TemplateResponse(
        "pages/register.html",
        {"request": request, "error": error, **register_form.model_dump()},
        block_name="register_form",
    )


@router.get("/login")
async def login(request: Request):
    return templates.TemplateResponse("pages/login.html", {"request": request})


@router.post("/login")
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

    return await login_user(request, user)


async def login_user(request: Request, user: User):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = access_token_security.create_access_token(
        subject=jsonable_encoder(AuthTokenPayload(id=user.id)),
        expires_delta=access_token_expires,
    )
    access_token_security.set_access_cookie(response, token, access_token_expires)
    # redirect user to the dashboard
    response.headers["HX-Redirect"] = str(request.url_for("dashboard"))
    return Response(headers=response.headers)


@router.get("/logout")
async def logout(request: Request):
    # clear cookie
    response = RedirectResponse(url="/")
    access_token_security.unset_access_cookie(response)
    return response


@router.get("/forgot-password")
async def forgot_password(request: Request):
    return templates.TemplateResponse(
        "pages/forgot_password.html", {"request": request}
    )


@router.post("/forgot-password")
async def forgot_password_post(
        request: Request, user_service: UserServiceDep, email: str = Form()
):
    error = None
    success = None
    try:
        await user_service.recover_password(email=email)
        success = f"An email was sent to {email}"
    except UserNotFoundError as e:
        error = e.args[0]
    return templates.TemplateResponse(
        "pages/forgot_password.html",
        {"request": request, "error": error, "success": success},
        block_name="forgot_password_form",
    )


@router.get("/reset-password")
async def reset_password(request: Request, token: str):
    context = {"request": request}
    email = verify_password_reset_token(token=token)
    if not email:
        context["error"] = "Invalid token"

    context["token"] = token
    return templates.TemplateResponse("pages/reset_password.html", context)


@router.post("/reset-password")
async def reset_password_post(
        request: Request,
        user_service: UserServiceDep,
        token: str = Form(),
        new_password: str = Form(),
):
    context = {"request": request}
    email = verify_password_reset_token(token=token)
    if not email:
        context["error"] = "Invalid token"

    try:
        user = await user_service.get_user_by_email(email=email)
        updated_user = await user_service.update_user(
            user_id=user.id,
            update_dict={
                "password": new_password,
            },
        )
        context["success"] = "Your password has been updated!"
    except UserNotFoundError as e:
        context["error"] = e.args[0]

    if not user.is_active:
        context["error"] = "Your account is not active, please check your email"

    context["token"] = token
    return templates.TemplateResponse(
        "pages/reset_password.html", context, block_name="password_reset_form"
    )
