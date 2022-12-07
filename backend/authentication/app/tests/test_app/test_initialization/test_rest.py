import pytest
import requests
import pytest_check as check

from requests import Response
from fastapi import status



class TestLogin:

    def test_example(self, test_app):
        response = test_app.get("/api/auth/ping")
        assert response.status_code == 200
        assert response.json() == {"ping": "pong!"}

    def test_login(self, login):
        print(login.json())

    def test_registration_user(self, registration: Response):
        print(registration.json())
