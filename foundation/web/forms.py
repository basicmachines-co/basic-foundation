from typing import Sequence

from starlette_wtf import StarletteForm
from wtforms import StringField, PasswordField, validators
from wtforms import ValidationError
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import HiddenField

from foundation.core.users import StatusEnum, RoleEnum
from foundation.core.users.schemas import validate_password


def password_validator(form, field):
    try:
        validate_password(field.data)
    except ValueError as e:
        raise ValidationError(str(e))


def choices_list(values: Sequence[str]):
    choices = [(val, val.capitalize()) for val in values]
    return [(" ", " ")] + choices


def password_2_validator(form, field):
    if field.data != form.password.data:
        # Add error to both password_1 and password_2 fields
        form.password.errors.append("Passwords do not match.")
        raise ValidationError("Passwords do not match.")


def password_validator_admin(form, field):
    """
    Only require validation if the password field is filled when editing via the admin ui
    :param field:
    :return: None
    """
    #
    if form.password.data or form.password_2.data:
        if form.password.data != form.password_2.data:
            form.password.errors.append("Passwords do not match.")
            form.password_2.errors = ["Passwords do not match."]
            raise ValidationError("Passwords do not match.")


class LoginForm(StarletteForm):
    username = StringField(
        "Email address",
        [validators.DataRequired(), validators.Email()],
        id="username",
        render_kw={"placeholder": "your@email.com", "aria-label": "Email address"},
    )

    password = PasswordField(
        "Password",
        [validators.DataRequired()],
        id="password",
        render_kw={"placeholder": "••••••••"},
    )


class RegisterForm(StarletteForm):
    full_name = StringField(
        "Full Name",
        [validators.DataRequired(), validators.Length(min=2, max=100)],
        render_kw={"placeholder": "Full Name", "aria-label": "Full Name"},
    )
    email = StringField(
        "Email address",
        [validators.DataRequired(), validators.Email()],
        render_kw={"placeholder": "your@email.com", "aria-label": "Email address"},
    )
    password = PasswordField(
        "Password",
        [validators.DataRequired(), password_validator],
        render_kw={"placeholder": "••••••••"},
    )
    password_2 = PasswordField(
        "Repeat Password",
        [validators.DataRequired(), password_validator, password_2_validator],
        render_kw={"placeholder": "••••••••"},
    )


class UserCreateForm(RegisterForm):
    role = SelectField(
        "Role",
        choices=choices_list(RoleEnum.values()),
        validators=[validators.DataRequired()],
        description="Admins can edit other users",
    )


class UserEditForm(UserCreateForm):
    status = SelectField(
        "Status",
        choices=choices_list(StatusEnum.values()),
        validators=[validators.DataRequired()],
    )
    password = PasswordField("Password", [password_validator_admin])
    password_2 = PasswordField(
        "Repeat Password",
        [
            password_validator_admin,
        ],
    )


class ForgotPasswordForm(StarletteForm):
    email = StringField(
        "Email address",
        [validators.DataRequired(), validators.Email()],
        render_kw={"placeholder": "your@email.com", "aria-label": "Email address"},
    )


class ResetPasswordForm(StarletteForm):
    token = HiddenField("Token", [validators.DataRequired()])
    new_password = PasswordField(
        "New Password",
        [validators.DataRequired(), password_validator],
        render_kw={"placeholder": "••••••••"},
    )
