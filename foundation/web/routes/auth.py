from datetime import timedelta
from typing import Optional

from fastapi import Request, Response
from fastapi import status
from fastapi.encoders import jsonable_encoder
from foundation.core.users.deps import UserServiceDep
from foundation.core.users.models import User
from foundation.core.users.schemas import AuthTokenPayload
from foundation.core.users.services import UserCreateError, UserNotFoundError
from starlette.responses import RedirectResponse, HTMLResponse

from foundation.core.config import settings
from foundation.core.security import verify_password_reset_token
from foundation.web.deps import access_token_security
from foundation.web.forms import (
    RegisterForm,
    LoginForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from foundation.web.templates import templates, template, render
from foundation.web.utils import HTMLRouter, error_notification, notification

router = HTMLRouter()


@router.get("/register")
async def register_get(request: Request):
    """
    Handles GET request for the registration page

    :param request: HTTP request object
    :return: Renders the registration HTML page with a registration form
    """
    form = RegisterForm(request)
    return templates.TemplateResponse(
        "pages/register.html", dict(request=request, form=form)
    )


@router.post("/register")
async def register_post(
    request: Request,
    user_service: UserServiceDep,
):
    """
    Handles user registration via a POST request. Validates form data and creates a new user if validation passes. Logs in the user upon successful creation.

    :param request: The HTTP request object
    :param user_service: Service for user-related operations
    :return: An HTTP response, either rendering a form with errors or redirecting upon successful registration
    """
    form = await RegisterForm.from_formdata(request)

    if await form.validate():
        try:
            user = await user_service.create_user(create_dict=form.data)
            return await login_user(request, user)
        except UserCreateError as e:
            return error_notification(request, e.args[0])

    modal_component = render("auth.RegisterForm", form=form)
    return HTMLResponse(modal_component)


@router.get("/login")
async def login(request: Request):
    """
    Render a login page.

    :param request: The incoming HTTP request data.
    :return: Rendered login page with an empty login form.
    """
    form = LoginForm(request)
    return template(request, "pages/login.html", {"form": form})


@router.post("/login")
async def login_post(
    request: Request,
    user_service: UserServiceDep,
):
    """
    Handles user login by processing form data, validating credentials,
    and authenticating the user. Displays appropriate messages on error cases.

    :param request: HTTP request object containing form data
    :param user_service: Dependency for user authentication methods
    :return: Template with login form and notification if any error occurs
    """
    form = await LoginForm.from_formdata(request)
    if not await form.validate():
        component = render("auth.LoginForm", form=form)
        return HTMLResponse(
            component,
            # status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

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

    modal_component = render(
        "auth.LoginForm",
        form=form,
        notification={
            "error": True,
            "title": "Error",
            "message": message,
            "hx_swap_oob": True,
        },
    )
    return HTMLResponse(modal_component)


async def login_user(request: Request, user: User):
    """
    Logs in the user by creating an access token which is set as a cookie in the response.
    It sets an expiration time for the access token and adds a redirect header to the root page.

    :param request: FastAPI request object
    :param user: Authenticated User object
    :return: HTTP response object with an access token cookie and a redirect header
    """
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
    """
    Handles user logout by clearing the authentication cookie and redirecting to the homepage.

    :param request: FastAPI Request object
    :return: RedirectResponse to homepage

    Example:
        @router.get("/logout")
        async def logout(request: Request):
            # Invoke this function to logout a user
    """
    # clear cookie
    response = RedirectResponse(url="/")
    access_token_security.unset_access_cookie(response)
    return response


@router.get("/forgot-password")
async def forgot_password(request: Request):
    """
    Handles GET requests for the forgot password page.

    :param request: The HTTP request object
    :return: A rendered HTML page with the forgot password form
    """
    form = ForgotPasswordForm(request)
    return template(request, "pages/forgot_password.html", {"form": form})


@router.post("/forgot-password")
async def forgot_password_post(request: Request, user_service: UserServiceDep):
    """
    Handles the forgot password post request.
    Validates the form data and attempts to initiate the password recovery process using the provided email.

    :param request: The HTTP request object containing the data submitted by the user.
    :param user_service: Dependency injection for the user service, responsible for user-related operations.
    :return: The response template with appropriate feedback messages.
    """
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
    modal_component = render(
        "auth.ForgotPasswordForm",
        form=form,
        notification={
            "error": False,
            "title": "OK!",
            "message": f"An email was sent to {form.email.data}",
            "hx_swap_oob": True,
        },
    )
    return HTMLResponse(modal_component)


@router.get("/reset-password")
async def reset_password(request: Request, token: Optional[str] = None):
    """
    Handle the GET request for password reset.

    :param request: The request object containing the request metadata and data.
    :param token: Optional password reset token provided in the request.
    :return: Rendered HTML template for the password reset page with the token, any possible error, and the form.

    The function initializes a form for resetting the password. If a token is provided,
    it attempts to verify the token and retrieves the associated email.
    If the token is invalid, an error message is set.
    """
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
    """
    Handle password reset request. Validates form data, verifies the reset token,
    and updates the user's password if the token and form data are valid.

    :param request: HTTP request with form data to reset password
    :param user_service: Service dependency to interact with user data
    :return: HTML response with the outcome of the reset process

    Errors:
        - If form data is invalid, returns form errors.
        - If reset token is invalid, returns "Invalid token" error message.
        - If user is not found, returns "User not found" error message.
        - If user's account is not active, returns "Your account is not active" error message.
    """
    form = await ResetPasswordForm.from_formdata(request)

    if not await form.validate():
        return template(
            request, "partials/auth/reset_password_form.html", {"form": form}
        )

    # get the users email by verifying the token
    assert form.token.data is not None
    email = verify_password_reset_token(token=form.token.data)
    if not email:
        return HTMLResponse(
            render("auth.ResetPasswordForm", form=form, error="Invalid token")
        )

    try:
        user = await user_service.get_user_by_email(email=email)
        if not user.is_active:
            return HTMLResponse(
                render(
                    "auth.ResetPasswordForm",
                    form=form,
                    error="Your account is not active",
                )
            )

        await user_service.update_user(
            user_id=user.id,
            update_dict={
                "password": form.new_password.data,
            },
        )
        return HTMLResponse(
            render(
                "auth.ResetPasswordForm",
                form=form,
                success="Your password has been updated!",
            )
        )
    except UserNotFoundError as e:
        return HTMLResponse(
            render("auth.ResetPasswordForm", form=form, error=e.args[0])
        )
