from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import UserUpdate
from .services import UserStorage, UserAuthorisation
from ..config import database_config
from ..models import User

oauth2_scheme = HTTPBearer()


class UserHandler:

    def __init__(self):
        self._authentication = UserAuthorisation()
        self._storage = UserStorage()

    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> User:
        """
        Dependency, используется для получения текущего пользователя.

        :param credentials: токен доступа с данными текущего пользователя.
        :return: UserOut pydantic схема с данными текущего пользователя.
        """
        username = self._authentication.decode_token(credentials.credentials)
        current_user = await self._storage.get_user_by_username(username=username)
        return current_user

    async def update_current_user(self, db_user: User, user_info: UserUpdate) -> UserUpdate:
        updated_user = await self._storage.update(db_user, user_info)
        updated_user_schema = UserUpdate.from_orm(updated_user)
        return updated_user_schema

    async def set_new_photo(self, photo: bytes):
        pass

    async def set_new_password(self):
        pass

    async def restore_password_with_email(self):
        pass


worker = UserHandler()


class RoleRequired:
    """Класс для проверки роли пользователя. От роли пользователя зависит его уровень доступа"""

    def __init__(self, role: set):
        self.role = role
        self.roles: set = database_config.roles

    def __call__(self, user: User = Depends(worker.get_current_user)):
        if user.user_role.role not in self.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Недостаточно прав для получения доступа к этой странице")
