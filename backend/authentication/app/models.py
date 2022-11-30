import orm

from uuid import uuid4
from sqlalchemy.sql import func

from .database import database

models = orm.ModelRegistry(database=database.database_obj)


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
        "id": orm.UUID(primary_key=True, allow_null=False, default=uuid4()),
        "username": orm.String(unique=True, min_length=5, max_length=20),
        "email": orm.Email(unique=True, max_length=100),
        "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
        "nickname": orm.String(unique=True, max_length=50, allow_null=True),
        "first_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "last_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "created_at": orm.DateTime(default=func.now()),
        "updated_at": orm.DateTime(allow_null=True, default=None),
        "birthday": orm.DateTime(allow_null=True),
        "photo": orm.String(allow_null=True, max_length=500, default=None),
        # "verified": orm.Boolean(default=False),
        "user_role": orm.ForeignKey(Role, on_delete="CASCADE")
    }

# class User(orm.Model):
#     tablename = "users"
#     registry = models
#     fields = {
#         "id": orm.UUID(primary_key=True, allow_null=False, default=uuid4()),
#         "username": orm.String(unique=True, min_length=5, max_length=20, expirable=False, expires=func.now()),
#         "email": orm.Email(unique=True, max_length=100),
#         "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
#         "created_at": orm.DateTime(default=func.now()),
#         "updated_at": orm.DateTime(allow_null=True, default=None),
#         "verified": orm.Boolean(default=False),
#         "user_role": orm.ForeignKey(Role, on_delete="CASCADE")
#     }
#
#
# class PersonalData(orm.Model):
#     tablename = "personal_data"
#     registry = models
#     fields = {
#         "id": orm.Integer(primary_key=True, allow_null=False),
#         "first_name": orm.String(allow_null=True, min_length=1, max_length=50),
#         "last_name": orm.String(allow_null=True, min_length=1, max_length=50),
#         "birthday": orm.DateTime(allow_null=True),
#         "photo": orm.String(allow_null=True, max_length=500, default=None),
#         "nickname": orm.String(unique=True, max_length=50, allow_null=True),
#         "init_data": orm.ForeignKey(User, on_delete="CASCADE")
#     }
