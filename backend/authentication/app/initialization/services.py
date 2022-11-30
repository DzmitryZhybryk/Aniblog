"""
Модуль хранит в себе UserInitialization и UserStorage классы.
UserInitialization - класс, который инициализирует пользователя.
UserStorage - класс, который хранит данные пользователя и сзаимодействует с базой данных.
"""
from jose import jwt, JWTError
from time import time

from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError
from sqlite3 import IntegrityError
from orm.exceptions import NoMatch

from .schemas import UserRegistration, UserLogin, Token
from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config, database_config
from ..utils.email_sender import EmailSender
from ..utils.code_verification import verification_code
from ..utils.password_verification import Password
from ..utils.token import token_worker
from ..database import redis_database
from ..base_storages import BaseStorage


class UserInitialization:
    """
    Класс для инициализации пользователей в системе.
    """

    def __init__(self):
        self._redis_connect = redis_database
        self._user_model = User
        self._token_worker = token_worker

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
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный проверочный код")

        await self._redis_connect.delete_data(key=code)
        user = UserRegistration.parse_raw(user_info)
        return user

    async def authenticate(self, db_user: User, user: UserLogin) -> Token:
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
            raise UnauthorizedException

        access_token = await self._token_worker.create_access_token(username=db_user.username,
                                                                    role=db_user.user_role.role)
        refresh_token = await self._token_worker.create_refresh_token()

        token_schema: Token = Token(access_token=access_token, refresh_token=refresh_token)
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
            raise UnauthorizedException

        current_user_username = await self._redis_connect.hget_data(name=current_refresh_token, key="username")
        current_user_role = await self._redis_connect.hget_data(name=current_refresh_token, key="role")
        if not current_user_username or not current_user_role:
            raise UnauthorizedException

        new_access_token = self._token_worker.create_access_token(username=current_refresh_token,
                                                                  role=current_user_role)
        return new_access_token

    async def delete_refresh_token(self, refresh_token: str) -> None:
        """
        Метод удаляет refresh_token пользователя из базы данных redis.

        Args:
            refresh_token: refresh_token пользователя.

        """
        await self._redis_connect.delete_data(key=refresh_token)


class UserStorage(BaseStorage):
    """
    Класс для работы с базой данных PostgreSQL.
    """

    def __init__(self):
        self._user_model = User
        self._role_model = Role

    async def has_users(self) -> bool:
        """
        Метод проверяет, есть ли пользователи в базе данных.

        Returns:
            true если есть пользователи, false если нет.

        """
        user_count = await self._user_model.objects.first()
        return bool(user_count)

    async def has_roles(self) -> bool:
        """
        Метод проверяет, есть ли роли в базе данных.

        Returns:
            true если есть роли, false если нет.

        """
        roles_count = await self._role_model.objects.first()
        return bool(roles_count)

    async def create_initial_roles(self) -> None:
        """
        Метод создает роли в базе данных, если их нет.

        """
        if not await self.has_roles():
            for role in database_config.roles:
                await self._role_model.objects.create(role=role)

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
            initial_user_role = await self._role_model.objects.get(role="admin")
            await self._user_model.objects.create(username="admin", password=hashed_password,
                                                  user_role=initial_user_role,
                                                  email="test@mail.ru")

    async def _is_username_exist(self, username: str):
        try:
            await self._user_model.objects.get(username=username)
            if username:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Пользователь с username {username} уже существует!"
                )
        except NoMatch:
            return None

    async def _is_email_exist(self, email: str):
        try:
            await self._user_model.objects.get(email=email)
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

    async def create(self, user_data: UserRegistration) -> User:
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
            new_db_user_role = await self._role_model.objects.get(role="base_user")
            new_db_user = await self._user_model.objects.create(username=user_data.username, password=hashed_password,
                                                                user_role=new_db_user_role, email=user_data.email)
            return new_db_user
        except (UniqueViolationError, IntegrityError) as ex:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{ex}: Account already exist"
            )
