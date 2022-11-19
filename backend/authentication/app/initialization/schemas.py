from datetime import datetime
from pydantic import BaseModel, Field, Required, validator, EmailStr
from email_validator import validate_email

from humps import camelize


class UserLogin(BaseModel):
    username: str = Field(default=Required, min_length=5, max_length=20)
    password: str = Field(default=Required, min_length=5, max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin"
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True


class UserRegistration(UserLogin):
    confirm_password: str = Field(default=Required)
    email: str = Field(default=Required)

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "email": "example@mail.ru",
                "password": "123password",
                "confirm_password": "123password",
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True

    @validator("email", pre=True)
    def lowercase(cls, value: str) -> str:
        """Преобразует email в нижний регистр"""
        return value.lower()

    @validator("confirm_password")
    def passwords_match(cls, confirm_password: str, values: dict) -> str:
        if "password" in values and "confirm_password" in values and confirm_password != values['password']:
            raise ValueError('Пароли не совпадают!')
        return confirm_password

    @validator("email")
    def validate_email(cls, email: str) -> str:
        validate_email(email)
        return email


class UserRegistrationResponse(BaseModel):
    message: str = "Данные для подтверждения регистрации отправлены на электронную почту."
    username: str = Field(default=Required, min_length=5, max_length=20)
    email: str = Field(default=Required)

    class Config:
        schema_extra = {
            "example": {
                "message": "Данные для подтверждения регистрации отправлены на электронную почту.",
                "username": "admin",
                "email": "example@mail.ru"
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4"
                                "cCI6MTY2NjkzMzY5OH0.BnYgKdoD5uReamF8bKbNn0Thh0EfCqDYGMgVVUuh2uE",
                "token_type": "Bearer"
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True
