import sqlalchemy

from databases import Database
from .config import database_config

database = Database(database_config.database_url)
engine = sqlalchemy.create_engine(database_config.database_url)


async def connect_database():
    await database.connect()


async def disconnect_database():
    await database.disconnect()
