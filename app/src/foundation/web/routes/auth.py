from datetime import timedelta

from fastapi import Request, Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from starlette.responses import RedirectResponse

from foundation.core.config import settings
from foundation.core.security import verify_password_reset_token
from foundation.users.deps import UserServiceDep
from foundation.users.models import User
from foundation.users.schemas import AuthTokenPayload, UserCreate
from foundation.users.services import UserCreateError, UserNotFoundError
from foundation.web.deps import access_token_security
from foundation.web.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from foundation.web.templates import templates
from foundation.web.utils import HTMLRouter

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
    error = None

    if await form.validate():
        full_name = form.full_name.data
        email = form.email.data
        password = form.password.data

        try:
            register_form = UserCreate(
                full_name=full_name, email=email, password=password, is_active=True
            )
            user = await user_service.create_user(
                create_dict=register_form.model_dump()
            )
            return await login_user(request, user)
        except UserCreateError:
            error = "User already exists"

    return templates.TemplateResponse(
        "pages/register.html",
        dict(request=request, error=error, form=form),
        block_name="content",
    )


@router.get("/login")
async def login(request: Request):
    form = LoginForm(request)
    return templates.TemplateResponse(
        "pages/login.html",
        dict(
            request=request,
            form=form,
        ),
    )


@router.post("/login")
async def login_post(
    request: Request,
    user_service: UserServiceDep,
):
    form = await LoginForm.from_formdata(request)
    if await form.validate():
        user = await user_service.authenticate(
            email=form.username.data, password=form.password.data
        )

    if user is None or not user.is_active:
        return templates.TemplateResponse(
            "pages/login.html",
            dict(
                request=request,
                error="Incorrect Username or Password",
                status_code=401,
                form=form,
            ),
            block_name="content",
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
    return templates.TemplateResponse(
        "pages/forgot_password.html",
        dict(
            request=request,
            form=form,
        ),
    )


@router.post("/forgot-password")
async def forgot_password_post(request: Request, user_service: UserServiceDep):
    form = await ForgotPasswordForm.from_formdata(request)
    error = None
    success = None

    if form.validate():
        try:
            await user_service.recover_password(email=form.email.data)
            success = f"An email was sent to {form.email.data}"
        except UserNotFoundError as e:
            error = e.args[0]
    else:
        error = "Please provide a valid email address."

    return templates.TemplateResponse(
        "pages/forgot_password.html",
        dict(request=request, form=form, error=error, success=success),
        block_name="content",
    )


@router.get("/reset-password")
async def reset_password(request: Request, token: str):
    form = ResetPasswordForm(request)
    form.token.data = token
    email = verify_password_reset_token(token=token)
    return templates.TemplateResponse(
        "pages/reset_password.html",
        dict(
            request=request,
            token=token,
            error="Invalid token" if not email else None,
            form=form,
        ),
    )


@router.post("/reset-password")
async def reset_password_post(
    request: Request,
    user_service: UserServiceDep,
):
    form = await ResetPasswordForm.from_formdata(request)
    error = None
    success = None

    if await form.validate():
        email = verify_password_reset_token(token=form.token.data)
        if not email:
            error = "Invalid token"
        else:
            try:
                user = await user_service.get_user_by_email(email=email)
                if not user.is_active:
                    error = "Your account is not active"
                else:
                    updated_user = await user_service.update_user(
                        user_id=user.id,
                        update_dict={
                            "password": form.new_password.data,
                        },
                    )
                    success = "Your password has been updated!"
            except UserNotFoundError as e:
                error = e.args[0]

    return templates.TemplateResponse(
        "pages/reset_password.html",
        dict(
            request=request,
            form=form,
            error=error,
            success=success,
        ),
        block_name="password_reset_form",
    )
