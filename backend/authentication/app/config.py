from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent.parent


class DatabaseConfig(BaseSettings):
    roles: set = {"admin", "moderator", "base_user"}

    database_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_hostname: str
    database_url: str

    redis_host: str
    redis_username: str
    redis_password: str
    redis_initialization_db: int
    redis_rout_cache_db: int
    redis_qwery_cache_db: int
    expire_verification_code_time: int  # second
    socket_connect_timeout: float = 0.1
    redis_hash_key: str
    digestmod: str

    class Config:
        env_file = BASE_DIR / '.env'


class JWTConfig(BaseSettings):
    secret_key: str
    jwt_algorithm: str
    access_token_expire: int  # minutes
    refresh_token_expire: int  # days

    class Config:
        env_file = BASE_DIR / '.env'


class EmailSenderConfig(BaseSettings):
    smtp_server_host: str
    smtp_server_port: int = 587
    work_email: str
    email_password: str

    class Config:
        env_file = BASE_DIR / '.env'


class BaseConfig(BaseSettings):
    upper_bound: int = 1000
    lower_bound: int = 9999

    class Config:
        env_file = BASE_DIR / '.env'


database_config = DatabaseConfig()
jwt_config = JWTConfig()
email_sender_config = EmailSenderConfig()
base_config = BaseConfig()
