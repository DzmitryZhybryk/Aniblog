from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent

DATABASE_PATH = BASE_DIR / "db.sqlite3"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# DATABASE_URL = "postgresql://dzmitry_zhybryk:3050132596@localhost/aniblog_db"


class DatabaseConfig(BaseSettings):
    database_url: str = DATABASE_URL
    roles: list = {"admin", "moderator", "base_user"}


class DecodeConfig(BaseSettings):
    secret_key: str = 'nJ98h9ahAa8h3AH98ahw9dhapw1Hd8'
    algorithm: str = "HS256"
    access_token_expire_minute: int = 30


class EmailSenderConfig(BaseSettings):
    smtp_server_host: str = "smtppp.gmail.com"
    smtp_server_port: int = 587
    work_email: str = "mr.zhybryk@gmail.com"
    email_password: str = "gjovrgkjcxurtztj"


database_config = DatabaseConfig()
decode_config = DecodeConfig()
email_sender_config = EmailSenderConfig()
