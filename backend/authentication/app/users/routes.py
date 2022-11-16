from fastapi import APIRouter, Depends

from ..config import database_config
from . import dependency, schemas
from ..models import User
from .services import user_services

router = APIRouter()


@router.post("/register/", tags=["Initialization"], response_model=schemas.UserRegistrationResponse)
async def registration(user: schemas.UserRegistration):
    """Роут для регистрации новых пользователей"""
    response = await user_services.registrate(user)
    return response


@router.post("/register/confirm/",
             response_model=schemas.Token,
             tags=["Initialization"])
async def confirm_registration(code: int):
    """Роут для подтверждения регистрации новых пользователей"""
    token = await user_services.validate_user_registration(code)
    return token


@router.post("/token/",
             response_model=schemas.Token,
             tags=["Initialization"])
async def login_user(user: schemas.UserLogin):
    """Роут для логина пользователей"""
    token = await user_services.login(user)
    return token


@router.get("/me/",
            response_model=schemas.UserOut,
            dependencies=[Depends(dependency.RoleRequired(database_config.roles))],
            tags=["User"])
async def current_user(user: User = Depends(dependency.get_current_user)):
    """Роут для получения информации о текущем пользователе"""
    return schemas.UserOut(
        username=user.username, first_name=user.first_name, last_name=user.last_name, nickname=user.nickname,
        email=user.email, birthday=user.birthday, user_role=user.user_role.role, created_at=user.created_at
    )


@router.put("/me/",
            response_model=schemas.UserUpdate,
            dependencies=[Depends(dependency.RoleRequired(database_config.roles))],
            tags=["User"])
async def current_user_update(user_data: schemas.UserUpdate, user: User = Depends(dependency.get_current_user)):
    """Роут для изменения данных текущего пользователя"""
    updated_user = await user_services.update_current_user(user, user_data)
    return updated_user
