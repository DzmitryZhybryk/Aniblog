from pydantic import BaseModel
from .responses import IncorrectLogin
from typing import Type


class CustomException(Exception):
    pass


class UnauthorizedException(CustomException):
    detail: BaseModel

    def __init__(self, *args, detail: BaseModel | Type[BaseModel] | None = None, **detail_kwargs):
        super().__init__(*args)
        self.detail = detail(**detail_kwargs) if detail and not isinstance(detail, BaseModel) else detail


class RedisConnectionError(CustomException):

    def __str__(self):
        return "Ошибка подключения к Redis"
