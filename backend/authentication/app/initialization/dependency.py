from datetime import timedelta

from .schemas import UserBase, UserRegistration, Token
from .services import create_registration_user, create_access_token, get_user_by_username, is_verify_password
from ..config import config
from ..exception import UnauthorizedException


def _generate_token(user: UserBase) -> Token:
    """
    Функция для генерации токенов доступа

    :param user: pydantic model с данными пользователя
    :return: pydantic model с bearer access token
    """
    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    token_schema = Token(access_token=token, token_type="Bearer")

    return token_schema


async def registration_user(user: UserRegistration) -> Token:
    """
    Dependency, используется роутом для регистрации новых пользователей

    :param user: pydantic model с данными для регистрации нового пользователя
    :return: pydantic model с bearer access token
    """
    await create_registration_user(user)
    token_schema = _generate_token(user)

    return token_schema


async def authenticate_user(user: UserBase) -> Token:
    """
    Dependency, используется роутом для аутентификации новых пользователей

    :param user: pydantic model с данными для аутентификации пользователя
    :return: pydantic model с bearer access token
    """
    db_user = await get_user_by_username(user.username)
    if not is_verify_password(user.password, db_user.password):
        raise UnauthorizedException
    token_schema = _generate_token(user)

    return token_schema
