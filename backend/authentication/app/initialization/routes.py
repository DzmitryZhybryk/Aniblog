from fastapi import APIRouter

from . import schemas
from .oauth2 import worker

router = APIRouter()


@router.post("/register/", tags=["Init"], response_model=schemas.UserRegistrationResponse)
async def registration(user: schemas.UserRegistration) -> schemas.UserRegistrationResponse:
    """Роут для регистрации новых пользователей"""
    response: schemas.UserRegistrationResponse = await worker.user_registration(user)
    return response


@router.post("/register/confirm/", response_model=schemas.Token, tags=["Init"])
async def confirm_registration(code: int) -> schemas.Token:
    """Роут для подтверждения регистрации новых пользователей"""
    token: schemas.Token = await worker.validate_user_registration(code)
    return token


@router.post("/token/", response_model=schemas.Token, tags=["Init"])
async def login_user(user: schemas.UserLogin) -> schemas.Token:
    """Роут для логина пользователей"""
    token: schemas.Token = await worker.login(user)
    return token


@router.post("/refresh/", response_model=schemas.Token, tags=["Init"])
async def refresh_token(token: str) -> schemas.Token:
    """Роут для обновления токена пользователя"""
    token: schemas.Token = await worker.get_refresh_token(current_refresh_token=token)
    return token
