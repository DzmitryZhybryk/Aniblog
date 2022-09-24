from pydantic import BaseModel, Field, Required, ValidationError, validator


class UserBase(BaseModel):
    username: str = Field(default=Required, title="Enter your username", example="YourUsername", min_length=5,
                          max_length=20)
    password: str = Field(default=Required, title="Enter your password", example="PasswordExample", min_length=5,
                          max_length=50)


class UserRegistration(UserBase):
    confirm_password: str = Field(default=Required, title="Confirm your password", example="PasswordExample")

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v


class UserAllData(UserBase):
    first_name: str = Field(title="Real name", example="Dzmitry", default=None)
    last_name: str = Field(title="Real surname", example="Zybryk", default=None)
    birthday: str = Field(title="date of birth", example="14.10.1990", default=None)


class TokenData(BaseModel):
    access_token: str = Field(default=None,
                              example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkamlua3N0ZXIx"
                                      "IiwiZXhwIjoxNjYzNDk1NzMyfQ.orEjuixehR_1EbEu6GlC2rsmy0jgMPST_c0oTZ1hlao")
    token_type: str = Field(default="bearer")
    username: str = Field(example="YourUsername")

    class Config:
        orm_mode = True
