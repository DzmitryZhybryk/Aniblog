from pathlib import Path

from pydantic import BaseSettings

BASE_DIR = Path(__file__).parent


# DATABASE_PATH = BASE_DIR / "db.sqlite3"
# DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


class DatabaseConfig(BaseSettings):
    # database_url: str = DATABASE_URL
    roles: list = {"admin", "moderator", "base_user"}

    database_port: int = 6500
    postgres_user: str = "dzmitry_zhybryk"
    postgres_password: str = "3050132596"
    postgres_db: str = "aniblog_db"
    postgres_host: str = "postgres"
    postgres_hostname: str = "127.0.0.1"

    redis_host: str = "redis"
    redis_username: str = "dzmitry_zhybryk"
    redis_password: str = "3050132596"
    redis_db: int = 0

    class Config:
        env_file = "./.env"


class JWTConfig(BaseSettings):
    secret_key: str = 'nJ98h9ahAa8h3AH98ahw9dhapw1Hd8'
    jwt_algorithm: str = "HS256"
    access_token_expire: int = 30
    refresh_token_expire: int = 60

    JWT_PRIVATE_KEY = "LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlCT2dJQkFBSkJBSSs3QnZUS0FWdHVQYzEzbEFkVk94TlVmcWxzMm1SVmlQWlJyVFpjd3l4RVhVRGpNaFZuCi9KVHRsd3h2a281T0pBQ1k3dVE0T09wODdiM3NOU3ZNd2xNQ0F3RUFBUUpBYm5LaENOQ0dOSFZGaHJPQ0RCU0IKdmZ2ckRWUzVpZXAwd2h2SGlBUEdjeWV6bjd0U2RweUZ0NEU0QTNXT3VQOXhqenNjTFZyb1pzRmVMUWlqT1JhUwp3UUloQU84MWl2b21iVGhjRkltTFZPbU16Vk52TGxWTW02WE5iS3B4bGh4TlpUTmhBaUVBbWRISlpGM3haWFE0Cm15QnNCeEhLQ3JqOTF6bVFxU0E4bHUvT1ZNTDNSak1DSVFEbDJxOUdtN0lMbS85b0EyaCtXdnZabGxZUlJPR3oKT21lV2lEclR5MUxaUVFJZ2ZGYUlaUWxMU0tkWjJvdXF4MHdwOWVEejBEWklLVzVWaSt6czdMZHRDdUVDSUVGYwo3d21VZ3pPblpzbnU1clBsTDJjZldLTGhFbWwrUVFzOCtkMFBGdXlnCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0t"
    JWT_PUBLIC_KEY = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZ3d0RRWUpLb1pJaHZjTkFRRUJCUUFEU3dBd1NBSkJBSSs3QnZUS0FWdHVQYzEzbEFkVk94TlVmcWxzMm1SVgppUFpSclRaY3d5eEVYVURqTWhWbi9KVHRsd3h2a281T0pBQ1k3dVE0T09wODdiM3NOU3ZNd2xNQ0F3RUFBUT09Ci0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ=="


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
