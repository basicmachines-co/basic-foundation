from foundation.core.emails import (
    generate_test_email,
    send_email,
    generate_reset_password_email,
    generate_new_account_email,
)
from foundation.core.security import (
    generate_password_reset_token,
    verify_password_reset_token,
)
from utils import mock_emails_send


def test_send_test_email(unstub_mocks):
    mock_emails_send()

    email_response = send_email(
        email_to="to", subject="subject", html_content="<html/>"
    )
    assert email_response.status_code is 250


def test_generate_test_email():
    email_to = "test@test.com"
    email_data = generate_test_email(email_to=email_to)
    assert email_data is not None
    assert email_data.html_content is not None
    assert email_data.subject is not None


def test_generate_reset_password_email():
    email_to = "test@test.com"
    email_data = generate_reset_password_email(
        email_to=email_to, email="test@test.com", token="token"
    )
    assert email_data is not None
    assert email_data.html_content is not None
    assert email_data.subject is not None


def test_generate_new_account_email():
    email_to = "test@test.com"
    email_data = generate_new_account_email(
        email_to=email_to, username="test", password="password"
    )
    assert email_data is not None
    assert email_data.html_content is not None
    assert email_data.subject is not None


def test_password_reset_token():
    email = "test@test.com"
    reset_token = generate_password_reset_token(email)

    token_subject = verify_password_reset_token(reset_token)
    assert token_subject is not None
    assert token_subject == email
