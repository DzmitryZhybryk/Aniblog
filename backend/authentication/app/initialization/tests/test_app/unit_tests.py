import pytest

from requests import Response
from fastapi import status


class TestLogin:
    url = "/api/auth/token/"

    @pytest.mark.parametrize("test_user, url", [({"username": "admin", "password": "admin"}, url)])
    def test_admin_login_response(self, login_page: Response, test_user: dict, url: str):
        assert login_page.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("test_user, url", [({"username": "admin", "password": "admin"}, url)])
    def test_admin_login_response_data(self, login_page: Response, test_user: dict, url: str):
        pass
