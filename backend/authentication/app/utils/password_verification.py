from passlib.context import CryptContext

from ..exception import UnauthorizedException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Функция хэширует полученные данные

    :param password: str object для хэширования
    :return: str object с хэшированными данными
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Функция для верификации пароля

    :param plain_password: пароль из формы
    :param hashed_password: пароль из базы данных
    :return: True - если пароли совпадают и False - если нет
    """
    is_verify = pwd_context.verify(plain_password, hashed_password)
    if not is_verify:
        raise UnauthorizedException
    return is_verify
