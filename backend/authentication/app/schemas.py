from pydantic import BaseModel, Field, Required


class BaseUser(BaseModel):
    username: str = Field(default=Required, title="Username for login", example="mr.jibrik@mail.ru",
                          regex=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    password: str = Field(default=Required, example="Some difficult password")


class RegUser(BaseUser):
    confirm_password: str = Field(default=Required, example="Some difficult password")


class RegUserOut(BaseModel):
    username: str = Field()
    token: str
