
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import UserOut
from .services import UserAuthentication, UserStorage
from ..config import database_config
from ..models import User


oauth2_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> User:
    """
    Dependency, используется для получения текущего пользователя

    :param credentials: токен доступа с данными текущего пользователя
    :return: UserOut pydantic схема с данными текущего пользователя
    """
    authentication = UserAuthentication()
    storage = UserStorage()
    decoded_token = authentication.decode_token(credentials.credentials)
    current_user = await storage.get_user_by_username(username=decoded_token.username)
    return current_user


class RoleRequired:
    """Класс для проверки роли пользователя. От роли пользователя зависет его уровень доступа"""

    def __init__(self, role: set):
        self.role = role
        self.roles: set = database_config.roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.user_role.role not in self.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Недостаточно прав для получения доступа к этой странице")
