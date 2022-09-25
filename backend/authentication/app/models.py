import orm
import sqlalchemy

from datetime import datetime
from sqlalchemy import Integer, Column, String, DateTime
from sqlalchemy.sql import func

from .database import database
from .config import config

models = orm.ModelRegistry(database=database)

metadata = sqlalchemy.MetaData()


class User(orm.Model):
    tablename = "users"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "username": orm.String(unique=True, min_length=5, max_length=20),
        "password": orm.String(allow_blank=False, allow_null=False, max_length=500),
        "role": orm.String(max_length=10, default="user"),
    }


class PersonData(orm.Model):
    tablename = "person_data"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "first_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "last_name": orm.String(allow_null=True, min_length=1, max_length=50),
        "created_at": orm.DateTime(default=func.now()),
        "birthday": orm.DateTime(allow_null=True)
    }
