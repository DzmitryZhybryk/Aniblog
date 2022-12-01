"""
Модуль хранит в себе роуты, которые используются для инициализации пользователей

"""
from fastapi import APIRouter, status, Body

from .oauth2 import worker
from .schemas import UserRegistrationResponse, UserRegistration, Token, UserLogin

router = APIRouter()


@router.post("/register/", tags=["Initialization"], response_model=UserRegistrationResponse,
             status_code=status.HTTP_201_CREATED)
async def registration(user: UserRegistration) -> UserRegistrationResponse:
    """Роут для регистрации новых пользователей"""
    response: UserRegistrationResponse = await worker.user_registration(user)
    return response


@router.post("/register/confirm/", response_model=Token, tags=["Initialization"], status_code=status.HTTP_201_CREATED)
async def confirm_registration(code: int = Body(embed=True)) -> Token:
    """Роут для подтверждения регистрации новых пользователей"""
    token: Token = await worker.validate_user_registration(code)
    return token


@router.post("/token/", response_model=Token, tags=["Initialization"], status_code=status.HTTP_200_OK)
async def login_user(user: UserLogin) -> Token:
    """Роут для аутентификации пользователей"""
    token: Token = await worker.login(user)
    return token


@router.post("/refresh/", response_model=Token, tags=["Initialization"], status_code=status.HTTP_200_OK)
async def refresh_token(token: str = Body(embed=True)) -> Token:
    """Роут для обновления токена доступа пользователей"""
    token: Token = await worker.get_new_access_token(refresh_token=token)
    return token


@router.post("/logout/", tags=["Initialization"], status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Body(embed=True)) -> None:
    """Роут для выхода текущего пользователя из системы"""
    await worker.logout_user(refresh_token=token)
