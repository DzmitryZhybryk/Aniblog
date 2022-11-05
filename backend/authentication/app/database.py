from databases import Database
from .config import database_config

DATABASE_URL = f"postgresql://{database_config.postgres_user}:{database_config.postgres_password}@" \
               f"{database_config.postgres_hostname}:{database_config.database_port}/{database_config.postgres_db}"

database = Database(DATABASE_URL)


async def connect_database():
    await database.connect()


async def disconnect_database():
    await database.disconnect()
