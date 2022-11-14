import aioredis

from aioredis import Redis
from aioredis.exceptions import RedisError
from databases import Database

from .exception import RedisConnectionError
from .config import database_config

DATABASE_URL = f"postgresql://{database_config.postgres_user}:{database_config.postgres_password}@" \
               f"{database_config.postgres_host}/{database_config.postgres_db}"


class DatabaseWorker:

    def __init__(self, url: str):
        self.database_obj = Database(url)

    async def connect_database(self):
        await self.database_obj.connect()

    async def disconnect_database(self):
        await self.database_obj.disconnect()


class RedisWorker:
    def __init__(self, url: str, password: str, db: int, username: str = None):
        self.url = url
        self.password = password
        self.db = db
        self.username = username
        self._connection: Redis | None = None

    def connect(self):
        self._connection = aioredis.from_url(self.url, username=self.username, password=self.password, db=self.db,
                                             decode_responses=True)

    async def disconnect(self):
        if not self._connection:
            raise RedisConnectionError

        await self._connection.close()
        self._connection = None

    async def set_data(self, key: str, value: str) -> dict:
        if not self._connection:
            raise RedisConnectionError
        try:
            await self._connection.set(key, value)
            await self._connection.expire(key, database_config.expire_data_time)
            return {"message": "data has been added"}
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)

    async def get_data(self, key: str) -> dict:
        if not self._connection:
            raise RedisConnectionError

        try:
            data = await self._connection.get(key)
            return data
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)

    async def delete_data(self, key: str) -> dict:
        if not self._connection:
            raise RedisConnectionError

        try:
            await self._connection.delete(key)
            return {"message": "data has been deleted"}
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)


database = DatabaseWorker(DATABASE_URL)
redis_database = RedisWorker(url=f"{database_config.redis_host}",
                             password=f"{database_config.redis_password}",
                             db=database_config.redis_db)
