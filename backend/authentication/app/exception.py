class CustomException(Exception):
    pass


class UnauthorizedException(CustomException):
    pass


class RedisConnectionError(CustomException):

    def __str__(self):
        return "Ошибка подключения к Redis"
