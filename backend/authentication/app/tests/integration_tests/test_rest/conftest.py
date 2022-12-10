import pytest
# from starlette.testclient import TestClient
from fastapi.testclient import TestClient

from backend.authentication.app.main import app


@pytest.fixture(scope="session")
def test_app():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session")
def headers() -> dict:
    return {"accept": "application/json", "Content-Type": "application/json"}


@pytest.fixture
def login(test_app, headers: dict, test_user: dict):
    response = test_app.post('/api/auth/token/', headers=headers, json=test_user)
    return response


@pytest.fixture
def registration():
    pass
