from datetime import timedelta, datetime
from jose import jwt, JWTError
from time import time

from fastapi import HTTPException, status

from asyncpg.exceptions import UniqueViolationError
from orm.exceptions import NoMatch
from sqlite3 import IntegrityError

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config, database_config
from .schemas import UserRegistration, UserLogin, Token
from ..utils.email_sender import EmailSender
from ..utils.code_verification import verification_code
from ..utils.password_verification import Password
from ..database import redis_database


class UserInitialization:

    @staticmethod
    async def send_registration_code_to_email(user: UserRegistration) -> str:
        registration_code = verification_code.get_verification_code()
        await redis_database.set_data(key=registration_code, value=user.json())
        email = EmailSender(recipient=user.email, verification_code=registration_code)
        email.send_email()
        return f"Данные для продолжения регистрации были отправлены на почту {user.email}"

    @staticmethod
    async def validate_code(code: str) -> UserRegistration:
        user_info = await redis_database.get_data(key=code)
        if not user_info:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный проверочный код")
        await redis_database.delete_data(key=code)
        user = UserRegistration.parse_raw(user_info)
        return user

    async def generate_token_data(self, user: User) -> Token:
        """
        Функция для создания токенов доступа

        :param user: pydantic model с данными пользователя
        :return: Token pydantic схема с bearer access token
        """
        access_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
        refresh_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.refresh_token_expire)
        await user.user_role.load()
        access_token = self._create_access_token(
            data={"sub": user.username, "role": user.user_role.role, "exp": access_token_expires})
        refresh_token = self._create_access_token(data={"exp": refresh_token_expires})
        await redis_database.set_hset_data(key=refresh_token, username=user.username, role=user.user_role.role)
        token_schema = Token(access_token=access_token, refresh_token=refresh_token)

        return token_schema

    @staticmethod
    def _create_access_token(data: dict) -> str:
        to_encode = data.copy()
        encode_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.jwt_algorithm)
        return encode_jwt

    async def authenticate(self, db_user: User, user: UserLogin) -> Token:
        """
        Функция для аутентификации пользователя
        """
        user_password = Password(password=user.password)
        if not user_password.verify_password(hashed_password=db_user.password):
            raise UnauthorizedException

        token_schema = await self.generate_token_data(db_user)
        return token_schema

    @staticmethod
    def _decode_refresh_token(refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
            if payload.get("exp") < int(time()):
                raise UnauthorizedException

            return refresh_token
        except JWTError:
            raise UnauthorizedException

    async def compare_refresh_token(self, current_refresh_token: str):
        access_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
        if not self._decode_refresh_token(refresh_token=current_refresh_token):
            raise UnauthorizedException

        current_user_username = await redis_database.hget_data(name=current_refresh_token, key="username")
        current_user_role = await redis_database.hget_data(name=current_refresh_token, key="role")
        if not current_user_username or not current_user_role:
            raise UnauthorizedException

        new_access_token = self._create_access_token(
            data={"sub": current_user_username, "role": current_user_role, "exp": access_token_expires})
        return new_access_token


class UserStorage:

    def __init__(self):
        self._user_model = User
        self._role_model = Role

    async def has_users(self) -> bool:
        """
        Функция проверяет наличие созданных пользователей в базе данных

        :return: bool object. True - если хотя бы один пользователь найден и False - если нет.
        """
        user_count = await self._user_model.objects.first()
        return bool(user_count)

    async def has_roles(self) -> bool:
        """
        Функция проверяет наличие созданных ролей в базе данных

        :return: bool object. True - если хотя бы одна роль найдена и False - если нет.
        """
        roles_count = await self._role_model.objects.first()
        return bool(roles_count)

    async def create_initial_roles(self) -> None:
        """Функция для создания ролей пользователей в базе данных"""
        if not await self.has_roles():
            for role in database_config.roles:
                await self._role_model.objects.create(role=role)

    async def create_initial_user(self) -> None:
        """Функция для создания первого пользователя при запуске приложения"""
        if not await self.has_roles():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Roles not found")

        if not await self.has_users():
            hashed_password = Password(password="admin").hash_password()
            initial_user_role = await self._role_model.objects.get(role="admin")
            await self._user_model.objects.create(username="admin", password=hashed_password,
                                                  user_role=initial_user_role,
                                                  email="test@mail.ru")

    async def get_user_by_username(self, username: str, raise_nomatch: bool = False) -> User | None:
        """
        Функция получает на вход имя пользователя, ищет его в базе данных и если находит, возвращает этого пользователя

        :param username: имя пользователя которого будем искать в базе данных
        :param raise_nomatch: если True - рейзит исключение, если пользователь не найден. Если False - возвращает None.
            По умолчанию False
        :return: объект класса User с данными пользователя из базы данных

        """
        try:
            user: User = await self._user_model.objects.get(username=username)
            await user.user_role.load()
            return user
        except NoMatch:
            if raise_nomatch:
                raise UnauthorizedException

    async def create(self, user_data: UserRegistration) -> User:
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
