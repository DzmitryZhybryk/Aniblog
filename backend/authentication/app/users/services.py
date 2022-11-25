from jose import jwt, JWTError
from time import time

from fastapi import HTTPException, status

from orm.exceptions import NoMatch

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config
from .schemas import UserUpdate


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

    @staticmethod
    def _is_birthday_exist(db_user: User) -> bool:
        if db_user.birthday:
            return True

    @staticmethod
    async def _is_nickname_exist(current_nickname: str, nickname: str) -> bool:
        try:
            if await User.objects.get(nickname=nickname) and current_nickname != nickname:
                return True

        except NoMatch:
            return False

    async def update(self, db_user: User, user_info: UserUpdate) -> User:
        try:
            # user_info.birthday = user_info.birthday if user_info.birthday else db_user.birthday
            # if user_info.birthday and self._is_birthday_exist(db_user):
            #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            #                         detail="День рождения можно поменять один раз!")

            if await self._is_nickname_exist(current_nickname=db_user.nickname, nickname=user_info.nickname):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Пользователь с nickname {user_info.nickname} уже существует")

            await db_user.update(username=user_info.username, first_name=user_info.first_name,
                                 last_name=user_info.last_name, birthday=user_info.birthday,
                                 nickname=user_info.nickname)
            return db_user
        except NoMatch:
            raise UnauthorizedException

    async def load_user_photo(self, photo: bytes):
        pass
