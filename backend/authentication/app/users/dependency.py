from datetime import timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import UserBase, UserRegistration, Token, UserOut, TokenData, UserUpdate
from .services import create_access_token, get_user_by_username, \
    update_current_db_user_data, send_registration_code_to_email, create_registration_user
from ..config import database_config, jwt_config
from ..exception import UnauthorizedException
from ..utils.password_verification import verify_password
from ..models import User

oauth2_scheme = HTTPBearer()


def _generate_token_data(user: UserBase | User) -> Token:
    """
    Функция для создания токенов доступа

    :param user: pydantic model с данными пользователя
    :return: Token pydantic схема с bearer access token
    """
    access_token_expires = timedelta(minutes=jwt_config.access_token_expire)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    token_schema = Token(access_token=token, token_type="Bearer")

    return token_schema


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> UserOut:
    """
    Dependency, используется для получения текущего пользователя

    :param credentials: токен доступа с данными текущего пользователя
    :return: UserOut pydantic схема с данными текущего пользователя
    """
    try:
        payload = jwt.decode(credentials.credentials, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedException
        token_data = TokenData(username=username)
    except JWTError:
        raise UnauthorizedException
    current_user = await get_user_by_username(username=token_data.username)
    await current_user.user_role.load()
    if current_user is None:
        raise UnauthorizedException

    current_user_schema = UserOut(id=current_user.id, username=current_user.username,
                                  created_at=current_user.created_at, user_role=current_user.user_role.role,
                                  email=current_user.email, first_name=current_user.first_name,
                                  last_name=current_user.last_name, birthday=current_user.birthday)
    return current_user_schema


class RoleRequired:
    """Класс для проверки роли пользователя. От роли пользователя зависет его уровень доступа"""

    def __init__(self, role: set):
        self.role = role
        self.roles: set = database_config.roles

    def __call__(self, user: UserOut = Depends(get_current_user)):
        if user.user_role not in self.role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Недостаточно прав для получения доступа к этой странице")


async def registration_user(user: UserRegistration) -> None:
    """
    Dependency, используется для регистрации новых пользователей

    :param user: pydantic model с данными для регистрации нового пользователя
    :return: pydantic model с bearer access token
    """
    await send_registration_code_to_email(user)


async def confirm_registration_user(verification_code: int) -> Token:
    """
    Dependency, используется для подтверждения регистрации нового пользователя

    :param verification_code: код подтверждения с электронной почты нового пользователя
    :return: Toke pydantic schema с токеном доступа и его типом
    """
    user = await create_registration_user(code=verification_code)
    token_schema = _generate_token_data(user)

    return token_schema


async def authenticate_user(user: UserBase) -> Token:
    """
    Dependency, используется для аутентификации новых пользователей

    :param user: pydantic model с данными для аутентификации пользователя
    :return: Token pydantic схема с bearer access token
    """
    db_user = await get_user_by_username(user.username, raise_nomatch=True)
    if not verify_password(user.password, db_user.password):
        raise UnauthorizedException
    token_schema = _generate_token_data(user)

    return token_schema


async def update_current_user(user_info: UserUpdate,
                              current_user: UserUpdate = Depends(get_current_user)) -> UserUpdate:
    """
    Dependency, используется для обновления данных текущего пользователя

    :param user_info: UserUpdate pydantic схема с данными, которые надо обновить в базе данных
    :param current_user: данные о текущем пользователе
    :return: UserUpdate pydantic схема с обновленными данными текущего пользователя
    """
    updated_user = await update_current_db_user_data(current_user=current_user.username, user_info=user_info)
    updated_user_schema = UserUpdate.from_orm(updated_user)
    return updated_user_schema
