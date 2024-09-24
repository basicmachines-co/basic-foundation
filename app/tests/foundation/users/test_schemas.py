import pytest
from foundation.users.schemas import validate_password


@pytest.mark.parametrize(
    "password",
    [
        "ValidPass1!",  # Valid password
        "Short1!",  # Too short
        "nouppercase1!",  # No uppercase letter
        "NOLOWERCASE1!",  # No lowercase letter
        "NoDigits!",  # No digit
        "NoSpecialchars1"  # No special character
    ]
)
def test_validate_password(password: str):
    if password == "ValidPass1!":
        assert validate_password(password) == password
    else:
        with pytest.raises(ValueError):
            validate_password(password)


@pytest.mark.parametrize(
    "password,expected_exception",
    [
        ("Short1!", "Password must be at least 8 characters long."),
        ("nouppercase1!", "Password must contain at least one uppercase letter."),
        ("NOLOWERCASE1!", "Password must contain at least one lowercase letter."),
        ("NoDigits!", "Password must contain at least one digit."),
        ("NoSpecialchars1", "Password must contain at least one special character.")
    ]
)
def test_validate_password_exceptions(password: str, expected_exception: str):
    with pytest.raises(ValueError) as excinfo:
        validate_password(password)
    assert str(excinfo.value) == expected_exception
