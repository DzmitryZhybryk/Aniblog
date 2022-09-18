from datetime import timedelta

from .schemas import UserBase, UserRegistration
from fastapi import HTTPException, status
from .services import create_registration_user, create_access_token
from .config import config


async def registration_user(user: UserRegistration):
    new_user = await create_registration_user(user)
    if not new_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can not create new user")

    access_token_expires = timedelta(minutes=config.access_token_expire_minute)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    new_user.access_token = token
    new_user.token_type = "bearer"
    return new_user
