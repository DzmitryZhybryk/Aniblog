from .schemas import BaseUser, RegUser
from fastapi import HTTPException, status


async def registration(user_data: RegUser):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords are not the same")

    return user_data
