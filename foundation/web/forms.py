from typing import Sequence

from foundation.core.users import StatusEnum, RoleEnum
from starlette_wtf import StarletteForm
from wtforms import StringField, PasswordField, validators
from wtforms import ValidationError
from wtforms.fields.choices import SelectField

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
    username = StringField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField("Password", [validators.DataRequired()])


class RegisterForm(StarletteForm):
    full_name = StringField(
        "Full Name", [validators.DataRequired(), validators.Length(min=2, max=100)]
    )
    email = StringField("Email", [validators.DataRequired(), validators.Email()])
    password = PasswordField(
        "Password", [validators.DataRequired(), password_validator]
    )
    password_2 = PasswordField(
        "Repeat Password",
        [validators.DataRequired(), password_validator, password_2_validator],
    )


class UserCreateForm(RegisterForm):
    role = SelectField(
        "Role",
        choices=choices_list(RoleEnum.values()),
        validators=[validators.DataRequired()],
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
    email = StringField("Email", [validators.DataRequired(), validators.Email()])


class ResetPasswordForm(StarletteForm):
    token = StringField("Token", [validators.DataRequired()])
    new_password = PasswordField(
        "Password", [validators.DataRequired(), password_validator]
    )
