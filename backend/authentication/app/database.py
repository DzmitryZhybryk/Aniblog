import psycopg2
from sqlalchemy import create_engine
from .config import config

database = create_engine(config.database_url)


async def connect_database():
    await database.connect()


async def disconnect_database():
    await database.disconnect()
