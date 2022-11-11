from fastapi import APIRouter, Depends

from ..config import database_config
from . import dependency, schemas

router = APIRouter()


@router.post("/register/",
             tags=["Initialization"],
             dependencies=[Depends(dependency.registration_user)])
async def registration() -> dict:
    """Роут для регистрации новых пользователей"""
    return {"message": "Данные для подвтерждения регистрации отправлены на Ваш Email"}


@router.post("/register/confirm/",
             response_model=schemas.Token,
             tags=["Initialization"])
async def confirm_registration(token: schemas.Token = Depends(dependency.confirm_registration_user)) -> schemas.Token:
    """Роут для подтверждения регистрации новых пользователей"""
    return token


@router.post("/token/",
             response_model=schemas.Token,
             tags=["Initialization"])
async def login(token: schemas.Token = Depends(dependency.authenticate_user)) -> schemas.Token:
    """Роут для логина новых пользователей"""
    return token


@router.get("/me/",
            response_model=schemas.UserOut,
            dependencies=[Depends(dependency.RoleRequired(database_config.roles))],
            tags=["User"])
async def current_user(user: schemas.UserOut = Depends(dependency.get_current_user)) -> schemas.UserOut:
    """Роут для получения информации о текущем пользователе"""
    return user


@router.put("/me/",
            response_model=schemas.UserUpdate,
            dependencies=[Depends(dependency.RoleRequired(database_config.roles))],
            tags=["User"])
async def current_user_update(user: schemas.UserUpdate = Depends(dependency.update_current_user)) -> schemas.UserUpdate:
    """Роут для изменения данных текущего пользователя"""
    return user
