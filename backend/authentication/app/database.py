import sqlalchemy

from databases import Database
from .config import config

database = Database(config.database_url)
engine = sqlalchemy.create_engine(config.database_url)


async def connect_database():
    await database.connect()


async def disconnect_database():
    await database.disconnect()
