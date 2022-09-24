from datetime import timedelta

from .schemas import UserBase, UserRegistration
from fastapi import HTTPException, status, Depends
from .services import create_registration_user, create_access_token, get_current_user, get_user_by_username, \
    is_verify_password
from .config import config


async def registration_user(user: UserRegistration):
    db_user = await create_registration_user(user)
    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    db_user.access_token = token
    db_user.token_type = "bearer"
    return db_user


async def get_current_active_user(current_user: Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


async def authenticate_user(user: UserBase):
    db_user = await get_user_by_username(user.username)
    is_verify_password(user.password, db_user.password)
    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    db_user.access_token = token
    db_user.token_type = "bearer"
    return db_user
