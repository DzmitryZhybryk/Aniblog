from datetime import timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .schemas import UserBase, UserRegistration, Token, UserOut, TokenData
from .services import create_registration_user, create_access_token, get_user_by_username, is_verify_password
from ..config import config
from ..exception import UnauthorizedException

oauth2_scheme = HTTPBearer()


def _generate_token_data(user: UserBase) -> Token:
    """
    Функция для генерации токенов доступа

    :param user: pydantic model с данными пользователя
    :return: pydantic model с bearer access token
    """
    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    token_schema = Token(access_token=token, token_type="Bearer")

    return token_schema


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> UserOut:
    """
    Dependency, используется для получения текущего пользователя
    """
    try:
        payload = jwt.decode(credentials.credentials, config.secret_key, algorithms=[config.algorithm])
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
                                  created_at=current_user.created_at, user_role=current_user.user_role.role)
    return current_user_schema


class RoleRequired:

    def __init__(self, role):
        self.role = role
        self.roles = config.roles

    def __call__(self, user: UserOut = Depends(get_current_user)):
        if user.user_role != self.role and user.user_role in self.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough rights")


async def registration_user(user: UserRegistration) -> Token:
    """
    Dependency, используется для регистрации новых пользователей

    :param user: pydantic model с данными для регистрации нового пользователя
    :return: pydantic model с bearer access token
    """
    await create_registration_user(user)
    token_schema = _generate_token_data(user)

    return token_schema


async def authenticate_user(user: UserBase) -> Token:
    """
    Dependency, используется для аутентификации новых пользователей

    :param user: pydantic model с данными для аутентификации пользователя
    :return: pydantic model с bearer access token
    """
    db_user = await get_user_by_username(user.username)
    if not is_verify_password(user.password, db_user.password):
        raise UnauthorizedException
    token_schema = _generate_token_data(user)

    return token_schema
