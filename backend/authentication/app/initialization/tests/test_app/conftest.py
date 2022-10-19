import pytest
import requests

from fastapi.testclient import TestClient

from backend.authentication.app.main import app

client = TestClient(app)


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
