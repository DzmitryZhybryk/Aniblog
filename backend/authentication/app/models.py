import orm
import sqlalchemy

from sqlalchemy import Integer, Column, String

from .database import database
from .config import config

models = orm.ModelRegistry(database=database)

metadata = sqlalchemy.MetaData()


notest = sqlalchemy.Table(
    "users1",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String),
    Column("password", String),
    Column("role", String, default="user")
)


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "username": orm.String(unique=True, min_length=1, max_length=100),
        "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
        "role": orm.String(max_length=10, default="user"),
    }
