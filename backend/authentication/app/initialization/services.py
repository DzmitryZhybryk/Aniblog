"""
Модуль хранит в себе UserInitialization и UserStorage классы.
UserInitialization - класс, который инициализирует пользователя.
UserStorage - класс, который взаимодействует с базой данных.
"""
from sqlite3 import IntegrityError
import sqlalchemy
from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException, status
from orm.exceptions import NoMatch
from datetime import timedelta

from .schemas import UserRegistration, UserLogin, Token
from ..base_storages import BaseStorage
from ..config import database_config
from ..exception import UnauthorizedException
from ..database import RedisWorker, database
from ..models import user, role
from ..config import jwt_config
from ..utils.code_verification import verification_code
from ..utils.email_sender import EmailSender
from ..utils.password_verification import Password
from ..utils.token import TokenWorker
from ..responses import IncorrectLogin


class UserInitialization:
    """
    Класс для инициализации пользователей в системе.
    """

    def __init__(self, redis_connect: RedisWorker, token_worker: TokenWorker):
        self._redis_connect = redis_connect
        self._token_worker = token_worker
        self._user_model: sqlalchemy.Table = user

    async def _save_registration_data_to_redis(self, registration_code: str, user: UserRegistration) -> None:
        await self._redis_connect.set_data(key=registration_code, value=user.json(),
                                           expire=database_config.expire_verification_code_time)

    async def send_registration_code_to_email(self, user: UserRegistration) -> None:
        """
        Метод отправляет код подтверждения регистрации на электронную почту пользователя.

        Args:
            user: UserRegistration pydantic схема с данными пользователя.

        """
        registration_code = verification_code.get_verification_code()
        await self._save_registration_data_to_redis(registration_code=registration_code, user=user)
        email = EmailSender(recipient=user.email, verification_code=registration_code)
        email.send_email()

    async def validate_code(self, code: str) -> UserRegistration:
        """
        Метод проверяет код подтверждения регистрации, сравнивая его с кодом в базе данных redis.

        Args:
            code: введенный пользователем код подтверждения регистрации.

        Returns:
            UserRegistration pydantic схема с данными пользователя.

        Exceptions:
            HTTPException: Если код не найден в базе данных.

        """
        user_info = await self._redis_connect.get_data(key=code)
        if not user_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Неверный проверочный код")

        await self._redis_connect.delete_data(key=code)
        user = UserRegistration.parse_raw(user_info)
        return user

    async def save_user_data_to_redis(self, username: str, role: str, refresh_token: str) -> None:
        await self._redis_connect.hset_data(key=refresh_token, expire=timedelta(days=jwt_config.refresh_token_expire),
                                            username=username, role=role)

    async def authenticate(self, db_user, user: UserLogin) -> Token:
        """
        Метод проверяет пароль пользователя на соответствие с паролем в базе данных PostgreSQL.

        Args:
            db_user: User pydantic схема с данными пользователя из базы данных
            user: UserLogin pydantic схема с данными пользователя, который хочет авторизоваться

        Returns:
            Token pydantic схема с токенами пользователя

        Exceptions:
            UnauthorizedException: Если пароль не совпадает с паролем в базе данных.

        """
        user_password = Password(password=user.password)
        if not user_password.verify_password(hashed_password=db_user.password):
            raise UnauthorizedException(detail=IncorrectLogin)

        token_schema = await self._token_worker.get_token_schema(username=db_user.username, role=db_user.user_role,
                                                                 refresh_token=True, access_token=True)
        await self.save_user_data_to_redis(username=db_user.username, role=db_user.user_role,
                                           refresh_token=token_schema.refresh_token)
        return token_schema

    async def compare_refresh_token(self, current_refresh_token: str):
        """
        Метод сравнивает refresh_token пользователя с refresh_token в базе данных redis.

        Args:
            current_refresh_token: текущий refresh_token пользователя.

        Returns:
            Новый access_token пользователя.

        Exceptions:
            UnauthorizedException: Если refresh_token не совпадает с refresh_token в базе данных.

        """
        if not self._token_worker.decode_refresh_token(refresh_token=current_refresh_token):
            raise UnauthorizedException(detail=IncorrectLogin)

        current_user_username = await self._redis_connect.hget_data(name=current_refresh_token, key="username")
        current_user_role = await self._redis_connect.hget_data(name=current_refresh_token, key="role")
        if not current_user_username or not current_user_role:
            raise UnauthorizedException(detail=IncorrectLogin)

        token_schema = await self._token_worker.get_token_schema(username=current_refresh_token,
                                                                 role=current_user_role, access_token=True)
        return token_schema

    async def delete_refresh_token(self, refresh_token: str) -> None:
        """
        Метод удаляет refresh_token пользователя из базы данных redis.

        Args:
            refresh_token: refresh_token пользователя.

        """
        await self._redis_connect.delete_data(key=refresh_token)


class UserStorage(BaseStorage):
    """
    Класс для работы с базой данных PostgresSQL.
    """

    def __init__(self):
        self._user_model: sqlalchemy.Table = user
        self._role_model: sqlalchemy.Table = role

    async def has_users(self) -> bool:
        """
        Метод проверяет, есть ли пользователи в базе данных.

        Returns:
            true если есть пользователи, false если нет.

        """
        qwery = self._user_model.select()
        users = await database.fetch_one(qwery)
        return bool(users)

    async def has_roles(self) -> bool:
        """
        Метод проверяет, есть ли роли в базе данных.

        Returns:
            true если есть роли, false если нет.

        """
        qwery = self._role_model.select()
        roles = await database.fetch_one(qwery)
        return bool(roles)

    async def create_initial_roles(self) -> None:
        """
        Метод создает роли в базе данных, если их нет.

        """
        if not await self.has_roles():
            for item in database_config.roles:
                qwery = self._role_model.insert().values(role=item)
                await database.execute(qwery)

    async def create_initial_user(self) -> None:
        """
        Метод создает init пользователя в базе данных, если его нет.

        Exceptions:
            HTTPException: Если роли не созданы.

        """
        if not await self.has_roles():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="В начале надо создать роли")

        if not await self.has_users():
            hashed_password = Password(password="admin").hash_password()
            qwery = self._role_model.select().where(self._role_model.c.role == "admin")
            user_role = await database.fetch_one(qwery)
            qwery = self._user_model.insert().values(username="admin", password=hashed_password, user_role=user_role.id,
                                                     email="test@mail.ru")
            await database.execute(qwery)

    async def _is_username_exist(self, username: str):
        try:
            qwery = self._user_model.select().where(self._user_model.c.username == username)
            username = await database.fetch_one(qwery)
            if username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с username {username} уже существует!"
                )
        except NoMatch:
            return None

    async def _is_email_exist(self, email: str):
        try:
            qwery = self._user_model.select().where(self._user_model.c.email == email)
            email = await database.fetch_one(qwery)
            if email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с электронной почтой {email} уже существует"
                )
        except NoMatch:
            return None

    async def check_registration_uniq_data(self, username: str, email: str) -> bool:
        if not await self._is_username_exist(username=username) and not await self._is_email_exist(email=email):
            return True

    async def create(self, user_data: UserRegistration):
        """
        Метод создает пользователя в базе данных postgresSQL.

        Args:
            user_data: данные пользователя.

        Returns:
            Созданный пользователь.

        Exceptions:
            HTTPException: Если пользователь с таким username уже существует.

        """
        hashed_password = Password(user_data.password).hash_password()
        try:
            qwery = self._role_model.select().where(self._role_model.c.role == "base_user")
            new_db_user_role = await database.fetch_one(qwery)
            qwery = self._user_model.insert().values(username=user_data.username, password=hashed_password,
                                                     user_role=new_db_user_role.id, email=user_data.email)
            new_db_user = await database.execute(qwery)
            return new_db_user
        except (UniqueViolationError, IntegrityError) as ex:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{ex}: Account already exist"
            )
