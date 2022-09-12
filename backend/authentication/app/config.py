from pathlib import Path

from pydantic import BaseSettings

DATABASE_URL = "postgresql://dzmitry_zhybryk:3050132596@localhost/aniblog_db"


class Config(BaseSettings):
    database_url: str = DATABASE_URL
    secret_key: str = '123'
    access_token_expire_minute: int = 30


config = Config()
