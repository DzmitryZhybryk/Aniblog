"""
Модуль хранит в себе UserInitialization и UserStorage классы.
UserInitialization - класс, который инициализирует пользователя.
UserStorage - класс, который хранит данные пользователя и сзаимодействует с базой данных.
"""
from datetime import timedelta, datetime
from jose import jwt, JWTError
from time import time

from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError
from sqlite3 import IntegrityError

from .schemas import UserRegistration, UserLogin, Token
from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config, database_config
from ..utils.email_sender import EmailSender
from ..utils.code_verification import verification_code
from ..utils.password_verification import Password
from ..database import redis_database
from ..base_storages import BaseStorage


class UserInitialization:
    """
    Класс для инициализации пользователей в системе.
    """

    def __init__(self):
        self._redis_connect = redis_database
        self._user_model = User

    async def send_registration_code_to_email(self, user: UserRegistration) -> None:
        """
        Метод отправляет код подтверждения регистрации на электронную почту пользователя.

        Args:
            user: UserRegistration pydantic схема с данными пользователя.

        """
        registration_code = verification_code.get_verification_code()
        await self._redis_connect.set_data(key=registration_code, value=user.json(),
                                           expire=database_config.expire_verification_code_time)
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

    async def generate_token_data(self, user: User) -> Token:
        """
        Метод генерирует токены для пользователя.

        Args:
            user: User pydantic схема с данными пользователя.

        Returns:
            Token pydantic схема с токенами пользователя.

        """
        access_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
        refresh_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.refresh_token_expire)
        await user.user_role.load()
        access_token = self._create_access_token(
            data={"sub": user.username, "role": user.user_role.role, "exp": access_token_expires})
        refresh_token = self._create_access_token(data={"exp": refresh_token_expires})
        await self._redis_connect.hset_data(key=refresh_token, expire=jwt_config.refresh_token_expire,
                                            username=user.username, role=user.user_role.role)
        token_schema = Token(access_token=access_token, refresh_token=refresh_token)
        return token_schema

    @staticmethod
    def _create_access_token(data: dict) -> str:
        """
        Метод создает токен для пользователя.

        Args:
            data: словарь с данными пользователя, которые будут закодированы в токене.

        Returns:
            токен пользователя.

        """
        to_encode = data.copy()
        encode_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.jwt_algorithm)
        return encode_jwt

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

        token_schema = await self.generate_token_data(db_user)
        return token_schema

    @staticmethod
    def _decode_refresh_token(refresh_token: str) -> str:
        """
        Метод декодирует refresh_token пользователя. Проверяет, что токен не истек.

        Args:
            refresh_token: refresh_token пользователя.

        Returns:
            refresh_token пользователя.

        Exceptions:
            UnauthorizedException: Eckb если токен истек.

        """
        try:
            payload = jwt.decode(refresh_token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
            if payload.get("exp") < int(time()):
                raise UnauthorizedException

            return refresh_token
        except JWTError:
            raise UnauthorizedException

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
        access_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
        if not self._decode_refresh_token(refresh_token=current_refresh_token):
            raise UnauthorizedException

        current_user_username = await self._redis_connect.hget_data(name=current_refresh_token, key="username")
        current_user_role = await self._redis_connect.hget_data(name=current_refresh_token, key="role")
        if not current_user_username or not current_user_role:
            raise UnauthorizedException

        new_access_token = self._create_access_token(
            data={"sub": current_user_username, "role": current_user_role, "exp": access_token_expires})
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

    async def create(self, user_data: UserRegistration) -> User:
        """
        Метод создает пользователя в базе данных postgreSQL.

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
