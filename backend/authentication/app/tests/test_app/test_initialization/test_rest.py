import pytest
import pytest_check as check

from requests import Response
from fastapi import status


class TestLogin:
    URL = "/api/auth/token/"

    @pytest.mark.parametrize("test_user, url", [({"username": "admin", "password": "admin"}, URL)])
    def test_admin_login_response(self, login_page: Response, test_user: dict, url: str):
        assert login_page.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("test_user, url", [({"username": "admin", "password": "admin"}, URL)])
    @pytest.mark.parametrize("expected_token_type", ["Bearer"])
    def test_admin_login_response_data(self, login_page: Response, test_user: dict, url: str, expected_token_type: str):
        response: dict = login_page.json()
        check.is_not_none(response.get("access_token"))
        check.equal(response.get("token_type"), expected_token_type)
