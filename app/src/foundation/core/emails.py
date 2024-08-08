from dataclasses import dataclass
from datetime import timedelta
from typing import Any, TypedDict

import emails  # type: ignore
from emails.backend.response import SMTPResponse
from jinja2 import Template
from jwt.exceptions import InvalidTokenError
from loguru import logger

from foundation.core.config import BASE_DIR
from foundation.core.config import settings
from foundation.core.security import reset_token


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
            BASE_DIR / "templates" / "email" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(
        *,
        email_to: str,
        subject: str = "",
        html_content: str = "",
) -> SMTPResponse:
    assert settings.emails_enabled, "no provided configuration for email variables"
    message = emails.Message(
        subject=subject,
        html=html_content,
        text="hello",
        mail_from=(settings.EMAIL_FROM_NAME, settings.EMAIL_FROM_EMAIL),
    )
    smtp_options = {"host": settings.EMAIL_SMTP_HOST, "port": settings.EMAIL_SMTP_PORT}
    if settings.EMAIL_SMTP_TLS:
        smtp_options["tls"] = True
    elif settings.EMAIL_SMTP_SSL:
        smtp_options["ssl"] = True
    if settings.EMAIL_SMTP_USER:
        smtp_options["user"] = settings.EMAIL_SMTP_USER
    if settings.EMAIL_SMTP_PASSWORD:
        smtp_options["password"] = settings.EMAIL_SMTP_PASSWORD
    response = message.send(to=email_to, smtp=smtp_options)
    logger.info(f"send email result: {response}")
    return response


def generate_test_email(email_to: str) -> EmailData:
    project_name = settings.app_name
    subject = f"{project_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"project_name": project_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    project_name = settings.app_name
    subject = f"{project_name} - Password recovery for user {email}"
    link = f"{settings.server_host}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "project_name": project_name,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
        email_to: str, username: str, password: str
) -> EmailData:
    project_name = settings.app_name
    subject = f"{project_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "project_name": settings.app_name,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.server_host,
        },
    )
    return EmailData(html_content=html_content, subject=subject)


class ResetTokenSubject(TypedDict):
    email: str


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    subject: ResetTokenSubject = {"email": email}
    return reset_token.create_access_token(subject=subject, expires_delta=delta)


def verify_password_reset_token(token: str) -> str | None:
    try:
        reset_token.jwt_backend.decode(token, settings.JWT_SECRET)
        decoded_token = reset_token.jwt_backend.decode(token, settings.JWT_SECRET)

        subject: ResetTokenSubject = decoded_token["subject"]
        return subject.get("email")
    except InvalidTokenError:
        return None