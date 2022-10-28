from datetime import datetime
from pydantic import BaseModel, Field, Required, validator


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", example="djinkster", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", example="123password", min_length=5,
                          max_length=50)


class UserRegistration(UserBase):
    email: str = Field(default=Required, title="Enter your email address", example="mr.jibrik@mail.ru")
    confirm_password: str = Field(default=Required, title="Confirm your password", example="123password")

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(example="admin")
    first_name: str | None = Field(example="Dzmitry")
    last_name: str | None = Field(example="Zhybryk")
    email: str | None = Field(example="example@mail.ru")
    birthday: datetime | None = Field(None, example="1990-10-14 15:41:39.641747")

    class Config:
        orm_mode = True


class UserOut(UserUpdate):
    user_role: str | None = Field(example="base_user")
    created_at: datetime | None = Field(example="2022-09-25 15:41:39.641747")

    class Config:
        orm_mode = True
