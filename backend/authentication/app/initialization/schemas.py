from pydantic import BaseModel, Field, Required, validator


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", example="admin", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", example="admin", min_length=5,
                          max_length=50)


class UserRegistration(UserBase):
    confirm_password: str = Field(default=Required, title="Confirm your password", example="admin")

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str
