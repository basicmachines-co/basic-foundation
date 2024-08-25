from starlette_wtf import StarletteForm
from wtforms import ValidationError, StringField, validators, PasswordField

from foundation.users.schemas import validate_password


def wtforms_password_validator(form, field):
    try:
        validate_password(field.data)
    except ValueError as e:
        raise ValidationError(str(e))


class LoginForm(StarletteForm):
    username = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [validators.DataRequired()])


class RegisterForm(StarletteForm):
    full_name = StringField('Full Name', [validators.DataRequired(), validators.Length(min=2, max=100)])
    email = StringField('Email', [validators.DataRequired(), validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        wtforms_password_validator
    ])


class ForgotPasswordForm(StarletteForm):
    email = StringField('Email', [validators.DataRequired(), validators.Email()])


class ResetPasswordForm(StarletteForm):
    token = StringField('Token', [validators.DataRequired()])
    new_password = PasswordField('Password', [
        validators.DataRequired(),
        wtforms_password_validator
    ])
