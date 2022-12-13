from datetime import timedelta, datetime

from fastapi import HTTPException, status
from orm.exceptions import NoMatch
import sqlalchemy
from .schemas import UserUpdate, PasswordUpdate
from ..base_storages import BaseStorage
from ..database import redis_qwery_cache_db, database
from ..models import user
from ..utils.password_verification import Password


class UserStorage(BaseStorage):

    def __init__(self):
        self._user_model: sqlalchemy.Table = user

    async def _is_nickname_exist(self, current_nickname: str, nickname: str) -> bool:
        try:
            qwery = self._user_model.select().where(self._user_model.c.nickname == nickname)
            if await database.execute(qwery) and current_nickname != nickname:
                return True

        except NoMatch:
            return False

    async def update_main_data(self, db_user, user_info: UserUpdate):
        try:
            if await self._is_nickname_exist(current_nickname=db_user.nickname, nickname=user_info.nickname):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Пользователь с nickname {user_info.nickname} уже существует")

            qwery = self._user_model.update().where(self._user_model.c.username == db_user.username).values(
                first_name=user_info.first_name, last_name=user_info.last_name, birthday=user_info.birthday,
                nickname=user_info.nickname, updated_at=datetime.now(), email=user_info.email)
            updated_user = await database.execute(qwery)
            await redis_qwery_cache_db.set(key=db_user.username, value=updated_user, expire=timedelta(hours=12))
            user_from_db = await self.get_user_by_username(username=db_user.username)
            return user_from_db
        except NoMatch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не найден")

    async def update_password(self, db_user, user_info: PasswordUpdate):
        try:
            new_password = Password(password=user_info.new_password).hash_password()
            qwery = self._user_model.update().where(self._user_model.c.username == db_user.username).values(
                password=new_password)
            updated_user = await database.execute(qwery)
            await redis_qwery_cache_db.set(key=db_user.username, value=updated_user)
        except NoMatch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не найден")

    async def load_user_photo(self, photo: bytes):
        pass
