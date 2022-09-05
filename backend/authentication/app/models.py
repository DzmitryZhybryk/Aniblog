import orm

from .database import database

models = orm.ModelRegistry(database=database)


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "username": orm.String(unique=True),
        "password": orm.String(allow_null=False),
        "role": orm.String(default="user")
    }
