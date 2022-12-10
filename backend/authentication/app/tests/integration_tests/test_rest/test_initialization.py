import pytest
import pytest_check as check

from requests import Response
from fastapi import status


@pytest.mark.usefixtures("login")
class TestLoginUser:

    @pytest.mark.integration
    @pytest.mark.parametrize("test_user", [{"username": "admin", "password": "admin"}])
    def test_login_init_user_response(self, test_user: dict):
        assert self.login.status_code == status.HTTP_200_OK, f"Status code is not {status.HTTP_200_OK}"

    @pytest.mark.integration
    @pytest.mark.parametrize("test_user", [{"username": "admin", "password": "admin"}])
    def test_login_init_user_response_data(self, login: Response, test_user: dict):
        check.is_not_none(login.json().get("accessToken")), f"Token is None"
        check.is_not_none(login.json().get("refreshToken")), f"Token is None"
        check.equal(login.json().get("tokenType"), "Bearer"), f"Token type is not bearer"


class TestRegistration:

    @pytest.mark.integration
    @pytest.mark.parametrize("test_user", [
        {"username": "djinkster", "password": "password", "confirm_password": "password",
         "email": "mr.jibrik@mail.ru"}])
    def test_registration_response(self):
        pass
