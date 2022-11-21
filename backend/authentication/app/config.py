from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent


class DatabaseConfig(BaseSettings):
    roles: set = {"admin", "moderator", "base_user"}

    database_port: int = 6500
    postgres_user: str = "dzmitry_zhybryk"
    postgres_password: str = "3050132596"
    postgres_db: str = "aniblog_db"
    postgres_host: str = "postgres"
    postgres_hostname: str = "127.0.0.1"

    redis_host: str = "redis://redis"
    redis_username: str = "dzmitry_zhybryk"
    redis_password: str = "3050132596"
    redis_db: int = 0
    expire_verification_code_time: int = 10800

    class Config:
        env_file = "./.env"


class JWTConfig(BaseSettings):
    secret_key: str = 'nJ98h9ahAa8h3AH98ahw9dhapw1Hd8'
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 15
    refresh_token_expire: int = 43200


class EmailSenderConfig(BaseSettings):
    smtp_server_host: str = "smtp.gmail.com"
    smtp_server_port: int = 587
    work_email: str = "mr.zhybryk@gmail.com"
    email_password: str = "gjovrgkjcxurtztj"


class BaseConfig(BaseSettings):
    upper_bound: int = 1000
    lower_bound: int = 9999


database_config = DatabaseConfig()
jwt_config = JWTConfig()
email_sender_config = EmailSenderConfig()
base_config = BaseConfig()
