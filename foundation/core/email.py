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
    """
    A data class to represent email content.

    Attributes:
    - html_content: The HTML content of the email.
    - subject: The subject of the email.

    Example usage:

        email_data = EmailData(
            html_content='<h1>Welcome</h1>',
            subject='Welcome to our service'
        )

    Error cases:
        Not raising any. Ensure to provide valid types for attributes.
    """

    html_content: str
    subject: str


def render_email_template(*, template_name: str, context: dict[str, Any]) -> str:
    """
    Renders an email template with the given context.

    :param template_name: Name of the template file.
    :param context: Dictionary containing variables to be substituted in the template.
    :return: Rendered HTML content as a string.

    Example usage:
        html_content = render_email_template(template_name="welcome.html", context={"username": "John Doe"})

    Error cases:
        Raises FileNotFoundError if the template file does not exist.
        Raises KeyError if any placeholders in the template are missing from the context.
    """
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
    """
    Sends an email with specified subject and HTML content.

    :param email_to: Email address of the recipient.
    :param subject: Subject of the email.
    :param html_content: HTML content of the email.
    :return: Instance of SMTPResponse if email is sent, otherwise None.

    Example usage:

        response = send_email(
            email_to='recipient@example.com',
            subject='Test Email',
            html_content='<h1>Hello</h1>'
        )
        if response:
            print("Email sent successfully.")
        else:
            print("Email sending is disabled.")
    """
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
    """
    :param email_to: Recipient's email address.
    :return: EmailData object containing the subject and HTML content of the test email.

    Creates a test email using a template and the application name. The template gets rendered with the app name and the recipient's email.
    Example:
        generated_email = generate_test_email("example@example.com")
    """
    app_name = settings.APP_NAME
    subject = f"{app_name} - Test email"
    html_content = render_email_template(
        template_name="test_email.html",
        context={"app_name": app_name, "email": email_to},
    )
    return EmailData(html_content=html_content, subject=subject)


def generate_reset_password_email(email_to: str, email: str, token: str) -> EmailData:
    """
    Generates an email for password recovery.

    :param email_to: Recipient's email address.
    :param email: User's email address.
    :param token: Password reset token.
    :return: An EmailData object containing the email content and subject.

    Example usage:
        email_data = generate_reset_password_email('recipient@example.com', 'user@example.com', 'token123')
        send_email(email_data)  # Hypothetical function to send the email

    Error cases:
        The function assumes valid input. Invalid email addresses or tokens
        might produce unexpected results. Ensure all settings (APP_NAME, server_host,
        EMAIL_RESET_TOKEN_EXPIRE_HOURS) are correctly configured.
    """
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
    """
    :param email_to: Recipient's email address.
    :param username: Username for the new account.
    :param password: Password for the new account.
    :return: EmailData object containing the email content and subject.

    Generates an email for a new account with user's credentials.

    Example usage:
        email = generate_new_account_email(
            email_to="user@example.com",
            username="new_user",
            password="secure_password"
        )
        send_email(email)
    """
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
