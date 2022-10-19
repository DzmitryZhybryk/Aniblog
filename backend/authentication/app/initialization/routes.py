from fastapi import APIRouter, Depends

from .schemas import Token
from .dependency import registration_user, authenticate_user

router = APIRouter()


@router.post("/registration/", response_model=Token)
async def registration(token: Token = Depends(registration_user)):
    """Роут для регистрации новых пользователей"""
    return token


@router.post("/token/", response_model=Token)
async def login(token: Token = Depends(authenticate_user)):
    """Роут для логина новых пользователей"""
    return token
