from jose import jwt, JWTError
from time import time
from datetime import timedelta, datetime

from fastapi import HTTPException, status

from orm.exceptions import NoMatch

from ..exception import UnauthorizedException
from ..models import User, Role
from ..config import jwt_config
from ..database import redis_qwery_cash_db
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


from ..base_storages import BaseStorage


class UserStorage(BaseStorage):

    def __init__(self):
        self._user_model = User

    @staticmethod
    def _is_birthday_exist(db_user: User) -> bool:
        if db_user.birthday:
            return True

    async def _is_nickname_exist(self, current_nickname: str, nickname: str) -> bool:
        try:
            if await self._user_model.objects.get(nickname=nickname) and current_nickname != nickname:
                return True

        except NoMatch:
            return False

    async def update(self, db_user: User, user_info: UserUpdate) -> User:
        try:
            if await self._is_nickname_exist(current_nickname=db_user.nickname, nickname=user_info.nickname):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Пользователь с nickname {user_info.nickname} уже существует")

            updated_user = await db_user.update(first_name=user_info.first_name,
                                                last_name=user_info.last_name, birthday=user_info.birthday,
                                                nickname=user_info.nickname, updated_at=datetime.utcnow())
            await redis_qwery_cash_db.set(key=db_user.username, value=updated_user, expire=timedelta(hours=12))
            return db_user
        except NoMatch:
            raise UnauthorizedException

    async def load_user_photo(self, photo: bytes):
        pass
