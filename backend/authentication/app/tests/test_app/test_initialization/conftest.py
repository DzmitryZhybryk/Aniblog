import pytest
import requests
from starlette.testclient import TestClient

from ....main import app


@pytest.fixture(scope="module")
def test_app():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def token(test_app):
    test_request_payload = {"username": "admin", "password": "admin"}
    response = test_app.post("/api/auth/token", json=test_request_payload)
    return response


@pytest.fixture
def registration(test_app):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    json_data = {
        'username': 'admin',
        'password': 'admin',
    }

    response = test_app.post('/api/auth/token/', headers=headers, json=json_data)
    return response


@pytest.fixture
def login(test_app):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
    }

    json_data = {
        'username': 'admin',
        'password': 'admin',
    }

    response = requests.post('http://127.0.0.1:8000/api/auth/token/', headers=headers, json=json_data)
    return response
