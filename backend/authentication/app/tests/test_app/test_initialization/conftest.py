import asyncio
import os

import pytest

from pathlib import Path
from fastapi.testclient import TestClient

CURRENT_DIR = Path(__file__).parent
os.environ['DATABASE_URL'] = f"sqlite:///{CURRENT_DIR / 'test_db.sqlite3'}"

from backend.authentication.app.models import models
from backend.authentication.app.database import connect_database, disconnect_database
from backend.authentication.app.main import app
from backend.authentication.app.users.services import has_db_user, create_initial_user, has_db_roles, create_users_roles

client = TestClient(app)


@pytest.fixture(scope="session")
async def on_startup() -> None:
    await models.create_all()
    await connect_database()

    db_has_roles = await has_db_roles()
    if not db_has_roles:
        await create_users_roles()

    db_has_user = await has_db_user()
    if not db_has_user:
        await create_initial_user()


@pytest.fixture(scope="session")
async def on_shutdown() -> None:
    await disconnect_database()


@pytest.fixture(scope="session", autouse=True)
def get_db(on_startup) -> None:
    asyncio.run(on_startup)
    # yield
    # if os.path.exists(path=f"{CURRENT_DIR}/test_db.sqlite3"):
    #     os.remove(path=f"{CURRENT_DIR}/test_db.sqlite3")


@pytest.fixture(scope="session")
def headers() -> dict:
    headers = {
        'accept': 'application/json',
    }
    return headers


@pytest.fixture(scope="function")
def login_page(headers: dict, url: str, test_user):
    response = client.post(url=url, headers=headers, json=test_user)
    return response


@pytest.fixture(scope="function")
def registration_page(headers: dict, url: str, test_user):
    response = client.post(url=url, headers=headers, json=test_user)
    return response
