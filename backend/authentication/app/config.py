from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent

DATABASE_PATH = BASE_DIR / "db.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# DATABASE_URL = "postgresql://dzmitry_zhybryk:3050132596@localhost/aniblog_db"


class Config(BaseSettings):
    database_url: str = DATABASE_URL
    secret_key: str = 'nJ98h9ahAa8h3AH98ahw9dhapw1Hd8'
    access_token_expire_minute: int = 30
    algorithm: str = "HS256"
    roles: list = {"admin", "moderator", "base_user"}


config = Config()
