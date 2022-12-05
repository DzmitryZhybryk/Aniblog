import asyncio
import os
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

CURRENT_DIR = Path(__file__).parent

os.environ['DATABASE_URL'] = f"sqlite:///{CURRENT_DIR / 'test_db.sqlite3'}"
# os.environ["STATIC_DIR"] = f"{Path(__file__).parent}"
# os.environ['SECRET_KEY'] = "5ae213a15b9c32174bb98388f6938d44c964645a3f493206db140ff92cf9ee6f"

from ....models import models
from ....database import database, redis_database
from ....initialization.services import UserStorage
from ....main import app

client = TestClient(app)


@pytest.fixture(scope="session")
async def on_startup() -> None:
    await models.create_all()
    await database.connect_database()
    redis_database.connect()

    storage = UserStorage()
    await storage.create_initial_roles()
    await storage.create_initial_user()


@pytest.fixture(scope="session")
async def on_shutdown() -> None:
    await database.disconnect_database()
    await redis_database.disconnect()


@pytest.fixture(scope="session", autouse=True)
def db_connection(on_startup) -> Generator:
    asyncio.run(on_startup)
    yield
    if os.path.exists(path=f"{CURRENT_DIR}/test_db.sqlite3"):
        os.remove(path=f"{CURRENT_DIR}/test_db.sqlite3")


@pytest.fixture(scope="session")
def headers() -> dict:
    headers = {"accept": "application/json"}
    return headers


@pytest.fixture
def registration(headers: dict, new_user_data: dict, url: str) -> Generator:
    response = client.post(url=url, headers=headers, json=new_user_data)
    yield response


@pytest.fixture
def token(headers: dict, test_user: dict, url: str):
    response = client.post(url=url, headers=headers, json=test_user)
    return response
