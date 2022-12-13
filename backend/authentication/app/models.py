import sqlalchemy
from uuid import uuid4
from sqlalchemy.sql import func
from .database import metadata

role = sqlalchemy.Table(
    "roles", metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("role", sqlalchemy.String(20), unique=True),
)

user = sqlalchemy.Table(
    "users", metadata,

    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("username", sqlalchemy.String(20), unique=True),
    sqlalchemy.Column("email", sqlalchemy.String(100), unique=True, nullable=False),
    sqlalchemy.Column("password", sqlalchemy.String(500), nullable=False),
    sqlalchemy.Column("nickname", sqlalchemy.String(50), unique=True, nullable=True),
    sqlalchemy.Column("first_name", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("last_name", sqlalchemy.String(50), nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, default=func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, nullable=True, default=None),
    sqlalchemy.Column("birthday", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("photo", sqlalchemy.String(500), nullable=True, default=None),
    sqlalchemy.Column("user_role", sqlalchemy.Integer, sqlalchemy.ForeignKey(role.c.id), nullable=False),
)
