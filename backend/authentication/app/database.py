from abc import ABC, abstractmethod

import aioredis
from aioredis import Redis
from aioredis.exceptions import RedisError
from cashews import Cache
from databases import Database
from datetime import timedelta

from .config import database_config
from .exception import RedisConnectionError

DATABASE_URL = f"postgresql://{database_config.postgres_user}:{database_config.postgres_password}@" \
               f"{database_config.postgres_host}/{database_config.postgres_db}"


class DatabaseWorker:

    def __init__(self, url: str):
        self.database_obj = Database(url)

    async def connect_database(self):
        await self.database_obj.connect()

    async def disconnect_database(self):
        await self.database_obj.disconnect()


def exceptions_handler(func):
    async def wrapper(self, *args, **kwargs):
        if not self._connection:
            raise RedisConnectionError

        try:
            data = await func(self, *args, **kwargs)
            return data
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)

    return wrapper


class RedisBase(ABC):

    @abstractmethod
    def __init__(self, url: str, password: str, db: int, username: str = None):
        self.url = url
        self.password = password
        self.db = db
        self.username = username
        self._connection: Redis | None = None

    def connect(self):
        self._connection = aioredis.from_url(self.url, username=self.username, password=self.password, db=self.db,
                                             decode_responses=True)

    @exceptions_handler
    async def disconnect(self):
        await self._connection.close()
        self._connection = None


class RedisWorker(RedisBase):
    def __init__(self, url: str, password: str, db: int, username: str = None):
        super().__init__(url, password, db, username)
        self._connection: Redis | None = None

    @exceptions_handler
    async def set_data(self, key: str, value: str, expire: int | None = None) -> None:
        await self._connection.set(key, value)
        await self._connection.expire(key, expire)

    @exceptions_handler
    async def hset_data(self, key: str, expire: timedelta | None = None, **kwargs):
        for item, value in kwargs.items():
            await self._connection.hset(key, item, value)
            await self._connection.expire(key, expire)

    @exceptions_handler
    async def get_data(self, key: str) -> dict:
        data = await self._connection.get(key)
        return data

    @exceptions_handler
    async def hget_data(self, name: str, key: str):
        data = await self._connection.hget(name=name, key=key)
        return data

    @exceptions_handler
    async def delete_data(self, key: str) -> None:
        await self._connection.delete(key)


database = DatabaseWorker(DATABASE_URL)

redis_database = RedisWorker(url=f"{database_config.redis_host}",
                             password=f"{database_config.redis_password}",
                             db=database_config.redis_initialization_db)

cache_router = Cache()
cache_router.setup(f"{database_config.redis_host}{database_config.redis_rout_cash_db}",
                   password=database_config.redis_password,
                   socket_connect_timeout=database_config.socket_connect_timeout, retry_on_timeout=True,
                   hash_key=database_config.redis_hash_key, digestmod=database_config.digestmod)

redis_qwery_cash_db = Cache()
redis_qwery_cash_db.setup(f"{database_config.redis_host}{database_config.redis_qwery_cash_db}",
                          password=database_config.redis_password,
                          socket_connect_timeout=database_config.socket_connect_timeout, retry_on_timeout=True,
                          hash_key=database_config.redis_hash_key, digestmod=database_config.digestmod)
