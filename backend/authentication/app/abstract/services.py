from jose import JWTError, jwt
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..exception import CredentialsException
from ..models import User
from ..config import config
from .schemas import TokenData, UserOut

oauth2_scheme = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> UserOut:
    try:
        payload = jwt.decode(credentials.credentials, config.secret_key, algorithms=[config.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException
        token_data = TokenData(username=username)
    except JWTError:
        raise CredentialsException
    current_user = await User.objects.get(username=token_data.username)
    await current_user.user_role.load()
    if current_user is None:
        raise CredentialsException

    current_user_schema = UserOut(id=current_user.id, username=current_user.username,
                                  created_at=current_user.created_at, user_role=current_user.user_role.role)
    return current_user_schema
