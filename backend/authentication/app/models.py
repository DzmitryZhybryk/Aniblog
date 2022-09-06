import orm

from .database import database

models = orm.ModelRegistry(database=database)


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "username": orm.String(unique=True, min_length=1, max_length=100),
        "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
        "role": orm.String(max_length=10, default="user"),
    }
