from datetime import timedelta, datetime

from fastapi import HTTPException, status
from orm.exceptions import NoMatch

from .schemas import UserUpdate, PasswordUpdate
from ..base_storages import BaseStorage
from ..database import redis_qwery_cache_db
from ..models import User
from ..utils.password_verification import Password


class UserStorage(BaseStorage):

    def __init__(self):
        self._user_model = User

    async def _is_nickname_exist(self, current_nickname: str, nickname: str) -> bool:
        try:
            if await self._user_model.objects.get(nickname=nickname) and current_nickname != nickname:
                return True

        except NoMatch:
            return False

    async def update_main_data(self, db_user: User, user_info: UserUpdate) -> User:
        try:
            if await self._is_nickname_exist(current_nickname=db_user.nickname, nickname=user_info.nickname):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=f"Пользователь с nickname {user_info.nickname} уже существует")

            updated_user = await db_user.update(first_name=user_info.first_name,
                                                last_name=user_info.last_name, birthday=user_info.birthday,
                                                nickname=user_info.nickname, updated_at=datetime.utcnow())
            await redis_qwery_cache_db.set(key=db_user.username, value=updated_user, expire=timedelta(hours=12))
            return db_user
        except NoMatch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не найден")

    async def update_password(self, db_user: User, user_info: PasswordUpdate):
        try:
            new_password = Password(password=user_info.new_password).hash_password()
            updated_user = await db_user.update(password=new_password)
            await redis_qwery_cache_db.set(key=db_user.username, value=updated_user)
        except NoMatch:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь не найден")

    async def load_user_photo(self, photo: bytes):
        pass
