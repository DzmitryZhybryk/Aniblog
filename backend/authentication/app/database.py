import aioredis

from aioredis.exceptions import RedisError
from databases import Database

from .config import database_config

DATABASE_URL = f"postgresql://{database_config.postgres_user}:{database_config.postgres_password}@" \
               f"{database_config.postgres_hostname}:{database_config.database_port}/{database_config.postgres_db}"


class DatabaseWorker(Database):

    def __init__(self, url: str):
        super().__init__(url)
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

    def get_connect(self):
        return aioredis.from_url(self.url, username=self.username, password=self.password, db=self.db)

    async def set_data(self, key: str, value: str) -> dict:
        try:
            await self.get_connect().set(key, value)
            return {"message": "data hase been added"}
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)
        finally:
            await self.get_connect().close()

    async def get_data(self, key: str) -> dict:
        try:
            data = await self.get_connect().get(key)
            return data
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)
        finally:
            await self.get_connect().close()

    async def delete_data(self, key: str) -> dict:
        try:
            await self.get_connect().delete(key)
            return {"message": "data hase been deleted"}
        except RuntimeError as ex:
            print(ex)
        except RedisError as ex:
            print(ex)
        finally:
            self.get_connect().close()


database = DatabaseWorker(DATABASE_URL)
redis_database = RedisWorker(url=f"{database_config.redis_host}",
                             password=f"{database_config.redis_password}",
                             db=f"{database_config.redis_db}")
