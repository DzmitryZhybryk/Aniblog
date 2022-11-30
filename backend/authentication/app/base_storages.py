from abc import ABC, abstractmethod
from datetime import timedelta

from orm.exceptions import NoMatch

from .models import User
from .database import redis_qwery_cash_db
from .exception import UnauthorizedException


class BaseStorage(ABC):

    @abstractmethod
    def __init__(self):
        self._user_model = User

    async def get_user_by_username(self, username: str, raise_nomatch: bool = False) -> User | None:
        try:
            user = await redis_qwery_cash_db.get(key=username)
            if not user:
                user: User = await self._user_model.objects.get(username=username)
                await user.user_role.load()
                await redis_qwery_cash_db.set(key=username, value=user, expire=timedelta(hours=12))

            return user
        except NoMatch:
            if raise_nomatch:
                raise UnauthorizedException
