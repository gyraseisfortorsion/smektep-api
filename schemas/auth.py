from pydantic import EmailStr, validator

from .base import Model


class LoginForm(Model):
    email: EmailStr
    password: str