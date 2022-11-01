from fastapi import APIRouter, Depends

from .schemas import Token, UserOut, UserUpdate
from .dependency import registration_user, authenticate_user, get_current_user, RoleRequired, update_current_user
from ..config import database_config

router = APIRouter()


@router.post("/registration/", response_model=Token, tags=["Initialization"])
async def registration(token: Token = Depends(registration_user)):
    """Роут для регистрации новых пользователей"""
    return token


@router.post("/token/", response_model=Token, tags=["Initialization"])
async def login(token: Token = Depends(authenticate_user)):
    """Роут для логина новых пользователей"""
    return token


@router.get("/me/", response_model=UserOut, dependencies=[Depends(RoleRequired(database_config.roles))], tags=["User"])
async def current_user(user: UserOut = Depends(get_current_user)):
    """Роут для получения информации о текущем пользователе"""
    return user


@router.put("/me/", response_model=UserUpdate, dependencies=[Depends(RoleRequired(database_config.roles))], tags=["User"])
async def current_user_update(user: UserUpdate = Depends(update_current_user)):
    """Роут для изменения данных текущего пользователя"""
    return user
