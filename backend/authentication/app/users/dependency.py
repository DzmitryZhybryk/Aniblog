from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import UserUpdate, PasswordUpdate
from .services import UserStorage
from ..config import database_config
from ..models import user
from ..utils.token import token

oauth2_scheme = HTTPBearer()


class UserHandler:

    def __init__(self):
        self._storage = UserStorage()
        self._token_worker = token

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)):
        """
        Dependency, используется для получения текущего пользователя.

        :param credentials: токен доступа с данными текущего пользователя.
        :return: UserOut pydantic схема с данными текущего пользователя.
        """
        username = self._token_worker.decode_token(credentials.credentials)
        current_user = await self._storage.get_user_by_username(username=username)
        return current_user

    async def update_current_user(self, db_user, user_info: UserUpdate):
        user_from_db = await self._storage.update_main_data(db_user, user_info)
        return user_from_db

    async def set_new_password(self, update_data: PasswordUpdate, user):
        await self._storage.update_password(db_user=user, user_info=update_data)


worker = UserHandler()


class RoleRequired:
    """Класс для проверки роли пользователя. От роли пользователя зависит его уровень доступа"""

    def __init__(self, role: set):
        self.role = role
        self.roles: set = database_config.roles

    def __call__(self, user=Depends(worker.get_current_user)):
        if user.user_role not in self.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Недостаточно прав для получения доступа к этой странице")
