from datetime import datetime
from pydantic import BaseModel, Field, Required, validator, EmailStr
from email_validator import validate_email, EmailNotValidError


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", min_length=5,
                          max_length=50)

    class Config:
        schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin"
            }
        }


class UserRegistration(UserBase):
    email: str = Field(default=Required, title="Enter your email address")
    confirm_password: str = Field(default=Required, title="Confirm your password")

    class Config(UserBase.Config):
        schema_extra = {
            "example": {
                "username": "djinkster",
                "password": "123password",
                "email": "mr.jibrik@mail.ru",
                "confirm_password": "123password"
            }
        }

    @validator("confirm_password")
    def passwords_match(cls, confirm_password, values):
        if "password" in values and "confirm_password" in values and confirm_password != values['password']:
            raise ValueError('Passwords do not match')
        return confirm_password

    @validator("email")
    def validate_email(cls, email):
        validate_email(email)
        return email


class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4"
                                "cCI6MTY2NjkzMzY5OH0.BnYgKdoD5uReamF8bKbNn0Thh0EfCqDYGMgVVUuh2uE",
                "token_type": "Bearer"
            }
        }


class TokenData(BaseModel):
    username: str | None = None

    class Config:
        schema_extra = {
            "example": {
                "username": "admin"
            }
        }


class UserUpdate(BaseModel):
    username: str | None
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    birthday: datetime | None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "admin",
                "first_name": "Dzmitry",
                "last_name": "Zhybryk",
                "email": "example@mail.ru",
                "birthday": "1990-10-14 15:41:39.641747"
            }
        }


class UserOut(UserUpdate):
    user_role: str | None
    created_at: datetime | None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "user_role": "base_user",
                "created_at": "2022-09-25 15:41:39.641747"
            }
        }
