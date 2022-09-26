from datetime import datetime
from pydantic import BaseModel, Field, Required, ValidationError, validator
from typing import Optional


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", example="admin", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", example="admin", min_length=5,
                          max_length=50)


class UserRegistration(UserBase):
    confirm_password: str = Field(default=Required, title="Confirm your password", example="PasswordExample")

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserPersonalData(BaseModel):
    first_name: str = Field(title="Real name", example="Dzmitry", default=None)
    last_name: str = Field(title="Real surname", example="Zybryk", default=None)
    birthday: datetime = Field(title="date of birth", example="2022-09-25 15:41:39.641747", default=None)
    created_at: datetime


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
