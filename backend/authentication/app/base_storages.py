from abc import ABC, abstractmethod
from datetime import timedelta, datetime

from orm.exceptions import NoMatch
import sqlalchemy
from .models import user
from .database import redis_qwery_cache_db, database
from .exception import UnauthorizedException
from .responses import IncorrectLogin
from pydantic import BaseModel


class AllUserData(BaseModel):
    id: str
    username: str
    email: str
    password: str
    nickname: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    created_at: datetime
    updated_at: datetime | None = None
    birthday: datetime | None = None
    photo: str | None = None
    user_role: int

    class Config:
        orm_mode = True


class BaseStorage(ABC):

    @abstractmethod
    def __init__(self):
        self._user_model: sqlalchemy.Table = user

    async def get_user_by_username(self, username: str, raise_nomatch: bool = False):
        try:
            user = await redis_qwery_cache_db.get(key=username)
            if not user:
                qwery = self._user_model.select().where(self._user_model.c.username == username)
                user = await database.fetch_one(qwery)
                user_schema: AllUserData = AllUserData.from_orm(user)
                await redis_qwery_cache_db.set(key=username, value=user_schema, expire=timedelta(hours=12))

            return user
        except NoMatch:
            if raise_nomatch:
                raise UnauthorizedException(detail=IncorrectLogin)
