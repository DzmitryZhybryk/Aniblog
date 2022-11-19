from jose import jwt, JWTError
from dataclasses import dataclass
from time import time

from fastapi import HTTPException, status

from orm.exceptions import NoMatch

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config
from .schemas import UserUpdate, TokenData


class UserAuthorisation:

    @staticmethod
    def decode_token(token: str) -> str:
        try:
            payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise UnauthorizedException

            if payload.get("exp") < int(time()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

            return username
        except JWTError:
            raise UnauthorizedException


class UserStorage:

    def __init__(self):
        self._user_model = User
        self._role_model = Role

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

    async def get_user_by_id(self, user_id: str, raise_nomatch: bool = False) -> User:
        try:
            user = await self._user_model.objects.get(id=user_id)
            return user
        except NoMatch:
            if raise_nomatch:
                raise HTTPException(status_code=404, detail="User not found")

    async def check_user_exists(self, username: str):
        db_user = await self.get_user_by_username(username=username)
        if db_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail=f"Account with username {username} already exist")

        return db_user

    @staticmethod
    def _is_birthday_exist(db_user: User) -> bool:
        """
        Функция проверяет, заполнено ли поле birthday в базе данных

        :param db_user: пользователь из базы данных
        :return: True, если поле birthday заполнено в базе данных и False, если нет
        """
        if db_user.birthday:
            return True

    async def update(self, db_user: User, user_info: UserUpdate) -> User:
        """
        Функция обновляет данные текущего пользователя в базе данных

        :param user_info: UserUpdate pydantic схема с данными, которые надо обновить в базе данных
        :return: объект класса User с обновленными данными пользователя из базы данных
        """
        try:
            if user_info.birthday and self._is_birthday_exist(db_user):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="День рождения можно поменять один раз!")

            await db_user.update(username=user_info.username, first_name=user_info.first_name,
                                 last_name=user_info.last_name, birthday=user_info.birthday)
            return db_user
        except NoMatch:
            raise UnauthorizedException
