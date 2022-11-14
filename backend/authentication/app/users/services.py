from datetime import timedelta, datetime
from jose import jwt

from fastapi import HTTPException, status

from asyncpg.exceptions import UniqueViolationError
from orm.exceptions import NoMatch
from sqlite3 import IntegrityError

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import database_config, jwt_config
from .schemas import UserRegistration, UserUpdate
from ..utils.email_sender import EmailSender
from ..utils.code_verification import verification_code
from ..utils.password_verification import hash_password
from ..database import redis_database


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


async def create_users_roles() -> None:
    """Функция для создания ролей пользователей в базе данных"""
    roles = database_config.roles
    for role in roles:
        await Role.objects.create(role=role)


async def create_initial_user() -> None:
    """Функция для создания первого пользователя при запуске приложения"""
    hashed_password = hash_password("admin")
    initial_user_role = await Role.objects.get(role="admin")
    await User.objects.create(username="admin", password=hashed_password, user_role=initial_user_role,
                              email="test@mail.ru", verified=True)


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
        expire = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.jwt_algorithm)
    return encode_jwt


async def _check_is_user_exist(username: str):
    db_user = await get_user_by_username(username=username)
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Account with username {username} already exist")
    return db_user


async def send_registration_code_to_email(user: UserRegistration) -> UserRegistration:
    if not await _check_is_user_exist(user.username):
        registration_code = verification_code.get_verification_code()
        await redis_database.set_data(key=registration_code, value=user.json())
        email = EmailSender(recipient=user.email, verification_code=registration_code)
        email.send_email()
        return user


async def _get_user_data_from_redis(code: int):
    user_data = await redis_database.get_data(key=code)
    if not user_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный проверочный код")
    return user_data


async def create_registration_user(code: int) -> User:
    user_data = await _get_user_data_from_redis(code=code)
    user = UserRegistration.parse_raw(user_data)
    redis_database.delete_data(key=code)
    hashed_password = hash_password(user.password)
    try:
        new_db_user_role = await Role.objects.get(role="base_user")
        new_db_user = await User.objects.create(username=user.username, password=hashed_password,
                                                user_role=new_db_user_role, email=user.email, verified=True)
        return new_db_user
    except (UniqueViolationError, IntegrityError) as ex:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{ex}: Account already exist"
        )


async def get_user_by_username(username: str, raise_nomatch: bool = False) -> User | None:
    """
    Функция получает на вход имя пользователя, ищет его в базе данных и если находит, возвращает этого пользователя

    :param username: имя пользователя которого будем искать в базе данных
    :param raise_nomatch: если True - рейзит исключение, если пользователь не найден. Если False - возвращает None.
        По умолчанию False
    :return: объект класса User с данными пользователя из базы данных
    """
    try:
        user: User = await User.objects.get(username=username)
        return user
    except NoMatch:
        if raise_nomatch:
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
                                    detail="День рождения можно поменять один раз!")

        await db_user.update(username=user_info.username, first_name=user_info.first_name,
                             last_name=user_info.last_name, birthday=user_info.birthday)
        return db_user
    except NoMatch:
        raise UnauthorizedException
