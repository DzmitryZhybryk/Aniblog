from datetime import timedelta

from .schemas import UserBase, UserRegistration, UserOut, UserOut, Token
from fastapi import HTTPException, status, Depends
from .services import create_registration_user, create_access_token, get_current_user, get_user_by_username, \
    is_verify_password
from .config import config
from .exception import UnauthorizedException


async def registration_user(user: UserRegistration):
    await create_registration_user(user)
    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    token_schema = Token(access_token=token, token_type="Bearer")

    return token_schema


async def get_current_active_user(current_user: UserOut = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def authenticate_user(user: UserBase):
    db_user = await get_user_by_username(user.username)
    if not is_verify_password(user.password, db_user.password):
        raise UnauthorizedException

    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    token_schema = Token(access_token=token, token_type="Bearer")

    return token_schema
