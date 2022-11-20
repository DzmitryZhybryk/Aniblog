"""
Модуль хранит в себе роуты, которые используются для инициализации пользователей

"""
from fastapi import APIRouter

from .schemas import UserRegistrationResponse, UserRegistration, Token, UserLogin
from .oauth2 import worker

router = APIRouter()


@router.post("/register/", tags=["Initialization"], response_model=UserRegistrationResponse)
async def registration(user: UserRegistration) -> UserRegistrationResponse:
    """Роут для регистрации новых пользователей"""
    response: UserRegistrationResponse = await worker.user_registration(user)
    return response


@router.post("/register/confirm/", response_model=Token, tags=["Initialization"])
async def confirm_registration(code: int) -> Token:
    """Роут для подтверждения регистрации новых пользователей"""
    token: Token = await worker.validate_user_registration(code)
    return token


@router.post("/token/", response_model=Token, tags=["Initialization"])
async def login_user(user: UserLogin) -> Token:
    """Роут для аутентификации пользователей"""
    token: Token = await worker.login(user)
    return token


@router.post("/refresh/", response_model=Token, tags=["Initialization"])
async def refresh_token(token: str) -> Token:
    """Роут для обновления токена доступа пользователей"""
    token: Token = await worker.get_new_access_token(refresh_token=token)
    return token


@router.get("/logout/", tags=["Initialization"])
async def logout():
    """Роут используется для окончания текущей сессии пользователя"""
    pass
