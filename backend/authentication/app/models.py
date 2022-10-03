import orm
import sqlalchemy

from sqlalchemy.sql import func

from .database import database

models = orm.ModelRegistry(database=database)

metadata = sqlalchemy.MetaData()


class Role(orm.Model):
    tablename = "roles"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "role": orm.String(max_length=20, unique=True)
    }


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "username": orm.String(unique=True, min_length=5, max_length=20),
        "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
        "first_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "last_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "created_at": orm.DateTime(default=func.now()),
        "birthday": orm.DateTime(allow_null=True),
        "picture_url": orm.String(allow_null=True, max_length=500, default=None),
        "user_role": orm.ForeignKey(Role, on_delete="CASCADE")
    }
