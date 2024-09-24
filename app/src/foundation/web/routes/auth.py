from datetime import timedelta
from typing import Optional

from fastapi import Request, Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from starlette.responses import RedirectResponse

from foundation.core.config import settings
from foundation.core.security import verify_password_reset_token
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.schemas import AuthTokenPayload
from foundation.users.services import UserCreateError, UserNotFoundError
from foundation.web.deps import access_token_security
from foundation.web.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from foundation.web.templates import templates, template
from foundation.web.utils import HTMLRouter, error_notification

router = HTMLRouter()


@router.get("/register")
async def register_get(request: Request):
    form = RegisterForm(request)
    return templates.TemplateResponse(
        "pages/register.html", dict(request=request, form=form)
    )


@router.post("/register")
async def register_post(
    request: Request,
    user_service: UserServiceDep,
):
    form = await RegisterForm.from_formdata(request)

    if await form.validate():
        try:
            user = await user_service.create_user(create_dict=form.data)
            return await login_user(request, user)
        except UserCreateError as e:
            return error_notification(request, e.args[0])

    return template(
        request,
        "partials/auth/register_form.html",
        {"form": form},
    )


@router.get("/login")
async def login(request: Request):
    form = LoginForm(request)
    return template(request, "pages/login.html", {"form": form})


@router.post("/login")
async def login_post(
    request: Request,
    user_service: UserServiceDep,
):
    form = await LoginForm.from_formdata(request)
    if not await form.validate():
        return template(request, "partials/auth/login_form.html", {"form": form})

    message = None
    assert form.username.data is not None
    assert form.password.data is not None
    user = await user_service.authenticate(
        email=form.username.data, password=form.password.data
    )
    if user and user.is_active:
        return await login_user(request, user)

    # if they can't be logged in show a message
    if user is None:
        message = "Incorrect email or password"
    elif not user.is_active:
        message = "Your account is not active"

    return template(
        request,
        "partials/auth/login_form.html",
        {
            "form": form,
            "notification": {
                "error": True,
                "title": "Error",
                "message": message,
                "hx_swap_oob": True,
            },
        },
    )


async def login_user(request: Request, user: User):
    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = access_token_security.create_access_token(
        subject=jsonable_encoder(AuthTokenPayload(id=user.id)),
        expires_delta=access_token_expires,
    )
    access_token_security.set_access_cookie(response, token, access_token_expires)
    # redirect user to the root page
    response.headers["HX-Redirect"] = str(request.url_for("index"))
    return Response(headers=response.headers)


@router.get("/logout")
async def logout(request: Request):
    # clear cookie
    response = RedirectResponse(url="/")
    access_token_security.unset_access_cookie(response)
    return response


@router.get("/forgot-password")
async def forgot_password(request: Request):
    form = ForgotPasswordForm(request)
    return template(request, "pages/forgot_password.html", {"form": form})


@router.post("/forgot-password")
async def forgot_password_post(request: Request, user_service: UserServiceDep):
    form = await ForgotPasswordForm.from_formdata(request)
    if not await form.validate():
        return template(
            request, "partials/auth/forgot_password_form.html", {"form": form}
        )

    assert form.email.data is not None
    try:
        await user_service.recover_password(email=form.email.data)
    except UserNotFoundError as e:
        return error_notification(request, e.args[0])

    # sends a sucess notification via hx-swap-oob
    return template(
        request,
        "partials/auth/forgot_password_form.html",
        {
            "form": form,
            "notification": {
                "title": "OK!",
                "message": f"An email was sent to {form.email.data}",
                "hx_swap_oob": True,
            },
        },
    )


@router.get("/reset-password")
async def reset_password(request: Request, token: Optional[str] = None):
    form = ResetPasswordForm(request)
    form.token.data = token

    email = None
    if token:
        email = verify_password_reset_token(token=token)
    error = "Invalid token" if not email else None
    return template(
        request,
        "pages/reset_password.html",
        {
            "token": token,
            "error": error,
            "form": form,
        },
    )


@router.post("/reset-password")
async def reset_password_post(
    request: Request,
    user_service: UserServiceDep,
):
    form = await ResetPasswordForm.from_formdata(request)

    if not await form.validate():
        return template(
            request, "partials/auth/reset_password_form.html", {"form": form}
        )

    # get the users email by verifying the token
    assert form.token.data is not None
    email = verify_password_reset_token(token=form.token.data)
    if not email:
        return template(
            request,
            "partials/auth/reset_password_form.html",
            {"error": "Invalid token"},
        )

    try:
        user = await user_service.get_user_by_email(email=email)
        if not user.is_active:
            return template(
                request,
                "partials/auth/reset_password_form.html",
                {"error": "Your account is not active"},
            )

        await user_service.update_user(
            user_id=user.id,
            update_dict={
                "password": form.new_password.data,
            },
        )
        return template(
            request,
            "partials/auth/reset_password_form.html",
            {"success": "Your password has been updated!"},
        )
    except UserNotFoundError as e:
        return template(
            request, "partials/auth/reset_password_form.html", {"error": e.args[0]}
        )
