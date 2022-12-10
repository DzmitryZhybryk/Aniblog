from pydantic import BaseModel


class UserAlreadyExists(BaseModel):
    detail: str = "Пользователь с такими данными уже существует"


class CodeNotFound(BaseModel):
    detail: str = "Проверочный код не найден"


class IncorrectLogin(BaseModel):
    detail: str = "Неверное имя пользователя или пароль"
