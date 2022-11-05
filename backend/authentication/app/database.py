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


database = DatabaseWorker(DATABASE_URL)
