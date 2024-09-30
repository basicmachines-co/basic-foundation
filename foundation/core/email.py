from dataclasses import dataclass
from typing import Any

import emails  # type: ignore
from emails.backend.response import SMTPResponse
from jinja2 import Template
from loguru import logger

from foundation.core.config import BASE_DIR
from foundation.core.config import settings


@dataclass
class EmailData:
    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    template_str = (
        BASE_DIR / "foundation" / "templates" / "email" / "build" / template_name
    ).read_text()
    html_content = Template(template_str).render(context)
    return html_content


def send_email(  # pragma: no cover
    *,
    email_to: str,
    subject: str,
    html_content: str,
) -> SMTPResponse | None:
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

    if settings.EMAIL_ENABLED:
        response = message.send(to=email_to, smtp=smtp_options)
        logger.info(f"send email {email_to} result: {response.__dict__}")
        return response
    else:
        logger.info(f"send email is disabled: {str(message)}")
        return None


def generate_test_email(email_to: str) -> EmailData:
    app_name = settings.APP_NAME
    subject = f"{app_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"app_name": app_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    app_name = settings.APP_NAME
    subject = f"{app_name} - Password recovery for user {email}"
    link = f"{settings.server_host}/reset-password?token={token}"
    html_content = render_email_template(
        template_name="reset_password.html",
        context={
            "app_name": app_name,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )
    logger.debug(f"Password reset link: {link}")
    return EmailData(html_content=html_content, subject=subject)


def generate_new_account_email(
    email_to: str, username: str, password: str
) -> EmailData:
    app_name = settings.APP_NAME
    subject = f"{app_name} - New account for user {username}"
    html_content = render_email_template(
        template_name="new_account.html",
        context={
            "app_name": settings.APP_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": settings.server_host,
        },
    )
    return EmailData(html_content=html_content, subject=subject)
