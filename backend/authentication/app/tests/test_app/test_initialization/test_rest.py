import pytest
import pytest_check as check

from requests import Response
from fastapi import status


class TestRegistration:
    URL = "/api/auth/registration/"

    @pytest.mark.anyio
    @pytest.mark.parametrize("new_user_data, url", [({"username": "djinkster",
                                                      "password": "123password",
                                                      "confirm_password": "123password",
                                                      "email": "jibrikdima@gmail.com"}, URL)])
    def test_registration_user(self, registration: Response, new_user_data: dict, url: str):
        assert registration.status_code == status.HTTP_201_CREATED

    # @pytest.mark.anyio
    # @pytest.mark.parametrize("new_user_data, url", [({"username": "djinkster",
    #                                                   "password": "123password",
    #                                                   "confirm_password": "123password",
    #                                                   "email": "mr.jibrik@mail.ru"}, URL)])
    # def test_registration_user_with_exist_username(self, registration: Response, new_user_data: dict, url: str):
    #     print(registration.json())

# class InitAdminUser:
#     URL = "/api/auth/token/"
#
#     @pytest.mark.anyio
#     @pytest.mark.parametrize("test_user, url", [({"username": "admin", "password": "admin"}, URL)])
#     def test_admin_login_response(self, token: Response, test_user: dict, url: str):
#         assert token.status_code == status.HTTP_200_OK
