from pydantic import BaseModel, Field, Required, ValidationError, validator


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", example="djinkster", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", example="Some difficult password",
                          min_length=5, max_length=20)

    @validator("username")
    def username_len(cls, v):
        min_length = 5
        max_length = 20
        if not min_length < len(v) < max_length:
            raise ValueError("Username should have max 20 and min 5 symbols")
        return v

    @validator("password")
    def password_len(cls, v):
        min_length = 5
        max_length = 20
        if not min_length < len(v) < max_length:
            raise ValueError("Password should have max 20 and min 5 symbols")
        return v


class UserRegistration(UserBase):
    confirm_password: str = Field(default=Required, title="Confirm your password", example="Some difficult password")

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserAllData(UserBase):
    first_name: str = Field(title="Real name", example="Dzmitry")
    last_name: str = Field(title="Real surname", example="Zybryk")
    birthday: str = Field(title="date of birth", example="14.10.1990")


class Token(BaseModel):
    access_token: str = None
    token_type: str = None


class TokenData(Token):
    username: str | None = None
