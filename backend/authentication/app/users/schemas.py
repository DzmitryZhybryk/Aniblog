from datetime import datetime

from pydantic import BaseModel, EmailStr, validator, validate_email

from humps import camelize


class PhotosDict:
    uuid: str
    url: str


class UserUpdate(BaseModel):
    username: str | None
    nickname: str | None
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    birthday: datetime | None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "admin",
                "nickname": "djinkster",
                "first_name": "Dzmitry",
                "last_name": "Zhybryk",
                "email": "example@mail.ru",
                "birthday": "1990-10-14 15:41:39.641747"
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True

    @validator("email")
    def validate_email(cls, email: str) -> str:
        """
        Тут должна быть документация
        Args:
            email:

        Returns:

        """
        validate_email(email)
        return email

    # @validator("nickname", pre=True)
    # def nickname_lowercase(cls, value: str):
    #     """
    #     Тут должна быть документация
    #     Args:
    #         value:
    #
    #     Returns:
    #
    #     """
    #     return value.lower()


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
        alias_generator = camelize
        allow_population_by_field_name = True
