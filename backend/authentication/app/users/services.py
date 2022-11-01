from datetime import timedelta, datetime
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

from asyncpg.exceptions import UniqueViolationError
from orm.exceptions import NoMatch
from sqlite3 import IntegrityError

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import database_config, decode_config
from .schemas import UserRegistration, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def has_db_user() -> bool:
    """
    Функция проверяет наличие созданных пользователей в базе данных

    :return: bool object. True - если хотя бы один пользователь найден и False - если нет.
    """
    user_count = await User.objects.first()
    return bool(user_count)


async def has_db_roles() -> bool:
    """
    Функция проверяет наличие созданных ролей в базе данных

    :return: bool object. True - если хотя бы одна роль найдена и False - если нет.
    """
    roles_count = await Role.objects.first()
    return bool(roles_count)


def _get_password_hash(password: str) -> str:
    """
    Функция хэширует полученные данные

    :param password: str object для хэширования
    :return: str object с хэшированными данными
    """
    return pwd_context.hash(password)


def is_verify_password(plain_password: str, hashed_password: str) -> bool:
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


async def create_users_roles() -> None:
    """Функция для создания ролей пользователей в базе данных"""
    roles = database_config.roles
    for role in roles:
        await Role.objects.create(role=role)


async def create_initial_user() -> None:
    """Функция для создания первого пользователя при запуске приложения"""
    hashed_password = _get_password_hash("admin")
    initial_user_role = await Role.objects.get(role="admin")
    await User.objects.create(username="admin", password=hashed_password, user_role=initial_user_role,
                              email="testk@mail.ru")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Функция для создания токена доступа

    :param data: dict с именем пользователя
    :param expires_delta: время жизни токена
    :return: access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=decode_config.access_token_expire_minute)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, decode_config.secret_key, algorithm=decode_config.algorithm)
    return encode_jwt


async def create_registration_user(user: UserRegistration) -> None:
    """
    Функция получает на вход pydantic model c данными нового пользователя и создаёт его в базе данных

    :param user: pydantic model с данными для регистрации нового пользователя
    :return: None
    """
    hashed_password = _get_password_hash(user.password)

    try:
        new_db_user_role = await Role.objects.get(role="base_user")
        await User.objects.create(username=user.username, password=hashed_password,
                                  user_role=new_db_user_role, email=user.email)
    except (UniqueViolationError, IntegrityError) as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{ex}",
            headers={"WWW-Authentication": "bearer"}
        )


async def get_user_by_username(username: str) -> User:
    """
    Функция получает на вход имя пользователя, ищет его в базе данных и если находит, возвращает этого пользователя

    :param username: имя пользователя которого будем искать в базе данных
    :return: объект класса User с данными пользователя из базы данных
    """
    try:
        user: User = await User.objects.get(username=username)
        return user
    except NoMatch:
        raise UnauthorizedException


def _is_birthday_exist(db_user: User) -> bool:
    """
    Функция проверяет, заполнено ли поле birthday в базе данных

    :param db_user: пользователь из базы данных
    :return: True, если поле birthday заполнено в базе данных и False, если нет
    """
    if db_user.birthday:
        return True


async def update_current_db_user_data(current_user: str, user_info: UserUpdate) -> User:
    """
    Функция обновляет данные текущего пользователя в базе данных

    :param current_user: имя текущего пользователя
    :param user_info: UserUpdate pydantic схема с данными, которые надо обновить в базе данных
    :return: объект класса User с обновленными данными пользователя из базы данных
    """
    try:
        db_user: User = await get_user_by_username(current_user)
        if user_info.birthday:
            if _is_birthday_exist(db_user):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="You can't change your birthday. Contact moderator")

        await db_user.update(username=user_info.username, first_name=user_info.first_name,
                             last_name=user_info.last_name, birthday=user_info.birthday)
        return db_user
    except NoMatch:
        raise UnauthorizedException
