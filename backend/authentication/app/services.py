from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError

from .models import User
from .config import config
from .schemas import UserBase, UserRegistration, TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


async def has_db_user() -> bool:
    user_count = await User.objects.first()
    return bool(user_count)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_initial_user():
    hashed_password = get_password_hash("admin")
    await User.objects.create(username="admin", password=hashed_password, role="admin")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, config.secret_key, algorithm=ALGORITHM)
    return encode_jwt


async def create_registration_user(user: UserRegistration):
    hashed_password = get_password_hash(user.password)

    try:
        new_db_user = await User.objects.create(username=user.username, password=hashed_password)
    except UniqueViolationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User with username '{user.username}' already exist")

    user_schema = TokenData.from_orm(new_db_user)
    return user_schema
