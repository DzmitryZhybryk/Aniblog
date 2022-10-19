from datetime import datetime
from pydantic import BaseModel, Field


class TokenData(BaseModel):
    username: str | None = None


class UserUpdate(BaseModel):
    username: str | None = Field(example="admin")
    user_role: str | None = Field(example="base_user")
    created_at: datetime | None = Field(example="2022-09-25 15:41:39.641747")
    first_name: str | None = Field(example="Dzmitry")
    last_name: str | None = Field(example="Zhybryk")
    birthday: datetime | None = Field(example="1990-10-14 15:41:39.641747")

    class Config:
        orm_mode = True


class UserOut(UserUpdate):
    id: int = Field(example="1")
