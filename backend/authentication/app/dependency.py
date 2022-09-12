from .schemas import UserBase, UserRegistration
from fastapi import HTTPException, status


async def registration_user(user: UserRegistration):
    return user
