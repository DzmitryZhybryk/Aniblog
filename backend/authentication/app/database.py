import psycopg2
from sqlalchemy import create_engine
from .config import Config

database = create_engine(Config.database_url)


async def connect_database():
    await database.connect()


async def disconnect_database():
    await database.disconnect()
