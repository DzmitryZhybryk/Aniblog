from pathlib import Path

from pydantic import BaseSettings

DATABASE_URL = "postgresql+psycopg2://dzmitry_zhybryk:3050132596@localhost/aniblog_db"


class Config(BaseSettings):
    database_url = DATABASE_URL
