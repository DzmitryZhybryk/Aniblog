from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi import HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from asyncpg.exceptions import UniqueViolationError
from orm.exceptions import NoMatch

from .exception import UnauthorizedException, CredentialsException
from .models import User, Role
from .config import config
from .schemas import UserBase, UserRegistration, TokenData, UserOut, UserOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
oauth2_scheme = HTTPBearer()


async def has_db_user() -> bool:
    user_count = await User.objects.first()
    return bool(user_count)


async def has_db_roles() -> bool:
    roles_count = await Role.objects.first()
    return bool(roles_count)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def is_verify_password(plain_password: str, hashed_password: str) -> bool:
    is_verify = pwd_context.verify(plain_password, hashed_password)
    if not is_verify:
        raise UnauthorizedException
    return is_verify


async def create_users_roles():
    roles = ["admin", "moderator", "base_user"]
    for role in roles:
        await Role.objects.create(role=role)


async def create_initial_user():
    hashed_password = get_password_hash("admin")
    initial_user_role = await Role.objects.get(role="admin")
    await User.objects.create(username="admin", password=hashed_password, user_role=initial_user_role)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=config.access_token_expire_minute)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, config.secret_key, algorithm=ALGORITHM)
    return encode_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(oauth2_scheme)) -> UserOut:
    try:
        payload = jwt.decode(credentials.credentials, config.secret_key, algorithms=[ALGORITHM])
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
                                  created_at=current_user.created_at, role=current_user.user_role.role)
    return current_user_schema


async def create_registration_user(user: UserRegistration):
    hashed_password = get_password_hash(user.password)

    try:
        new_db_user_role = await Role.objects.get(role="base_user")
        await User.objects.create(username=user.username, password=hashed_password,
                                  user_role=new_db_user_role)
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with username '{user.username}' already exist",
            headers={"WWW-Authentication": "bearer"}
        )

    return new_db_user_role


async def get_user_by_username(username: str):
    try:
        user = await User.objects.get(username=username)
        return user
    except NoMatch:
        raise UnauthorizedException
