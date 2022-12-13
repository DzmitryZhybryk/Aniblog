from datetime import datetime

from pydantic import BaseModel, EmailStr, validator, validate_email

from humps import camelize


class PhotosDict:
    id: str
    url: str


class UserUpdate(BaseModel):
    nickname: str | None
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    birthday: datetime | None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
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


class UserOut(UserUpdate):
    user_role: str | None
    created_at: datetime | None

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "admin",
                "nickname": "djinkster",
                "first_name": "Dzmitry",
                "last_name": "Zhybryk",
                "email": "example@mail.ru",
                "birthday": "1990-10-14 15:41:39.641747",
                "user_role": "base_user",
                "created_at": "2022-09-25 15:41:39.641747"
            }
        }
        alias_generator = camelize
        allow_population_by_field_name = True


class PasswordUpdate(BaseModel):
    new_password: str
    confirm_password: str

    @validator("confirm_password")
    def passwords_match(cls, confirm_password: str, values: dict) -> str:
        if "new_password" in values and confirm_password != values['new_password']:
            raise ValueError('Пароли не совпадают!')

        return confirm_password

    class Config:
        schema_extra = {
            "example": {
                "new_password": "StrongPassword",
                "confirm_password": "StrongPassword"
            }
        }
