from fastapi import APIRouter, Depends

from .schemas import Token, UserOut
from .dependency import registration_user, authenticate_user, get_current_user, RoleRequired

router = APIRouter()


@router.post("/registration/", response_model=Token, tags=["Initialization"])
async def registration(token: Token = Depends(registration_user)):
    """Роут для регистрации новых пользователей"""
    return token


@router.post("/token/", response_model=Token, tags=["Initialization"])
async def login(token: Token = Depends(authenticate_user)):
    """Роут для логина новых пользователей"""
    return token


@router.get("/me/", response_model=UserOut, dependencies=[Depends(RoleRequired("admin"))], tags=["User"])
async def me(user: UserOut = Depends(get_current_user)):
    """Роут для получения информации о текущем пользователе"""
    return user
