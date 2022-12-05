import asyncio
import os
from pathlib import Path
from typing import Generator

import pytest

CURRENT_DIR = Path(__file__).parent

os.environ['DATABASE_URL'] = f"sqlite:///{CURRENT_DIR / 'test_db.sqlite3'}"

from ...models import models
from ...database import database, redis_database
from ...initialization.services import UserStorage


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
