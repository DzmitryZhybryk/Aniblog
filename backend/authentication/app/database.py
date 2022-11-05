import aioredis

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
    def __init__(self, url: str, username: str, password: str, db: int):
        self.url = url
        self.username = username
        self.password = password
        self.db = db
        self.connect = aioredis.from_url(self.url, username=self.username, password=self.password, db=self.db)

    async def set_data(self, key: str, value: str) -> dict:
        try:
            await self.connect.set(key, value)
            return {"message": "data was added"}
        except Exception as ex:
            print(ex)
        finally:
            await self.connect.close()

    async def get_data(self, key: str) -> dict:
        try:
            data = await self.connect.get(key)
            return data
        except Exception as ex:
            print(ex)
        finally:
            self.connect.close()


database = DatabaseWorker(DATABASE_URL)
redis_database = RedisWorker(url="redis://localhost", username="admin", password="admin", db=0)
