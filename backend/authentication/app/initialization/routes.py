"""
Модуль хранит в себе роуты, которые используются для инициализации пользователей

"""
from fastapi import APIRouter, status, Body

from .oauth2 import worker
from .schemas import UserRegistrationResponse, UserRegistration, Token, UserLogin
from ..responses import UserAlreadyExists, CodeNotFound, IncorrectLogin

router = APIRouter()


@router.post("/registration/", tags=["Initialization"], response_model=UserRegistrationResponse,
             status_code=status.HTTP_201_CREATED,
             responses={201: {"description": "Успешное начало регистрации пользователя",
                              "model": UserRegistrationResponse},
                        409: {"description": "Попытка создания пользователя, который уже существует в базе данных",
                              "model": UserAlreadyExists}})
async def registration(user: UserRegistration) -> UserRegistrationResponse:
    """Роут для регистрации новых пользователей"""
    response: UserRegistrationResponse = await worker.user_registration(user)
    return response


@router.post("/registration/confirm/", response_model=Token, tags=["Initialization"],
             status_code=status.HTTP_201_CREATED,
             responses={201: {"description": "Успешная регистрация пользователя", "model": Token},
                        404: {"description": "Введён неверный проверочный код", "model": CodeNotFound}})
async def confirm_registration(code: int = Body(embed=True)) -> Token:
    """Роут для подтверждения регистрации новых пользователей"""
    token: Token = await worker.validate_user_registration(code)
    return token


@router.post("/token/", response_model=Token, tags=["Initialization"], status_code=status.HTTP_200_OK,
             responses={200: {"description": "Успешная авторизация пользователя", "model": Token},
                        401: {"description": "Попытка входа с неправильными данными", "model": IncorrectLogin}})
async def login_user(user: UserLogin) -> Token:
    """Роут для аутентификации пользователей"""
    token: Token = await worker.login(user)
    return token


@router.post("/refresh/", response_model=Token, tags=["Initialization"], status_code=status.HTTP_200_OK,
             responses={200: {"description": "Успешное обновление токена", "model": Token},
                        401: {"description": "Ввод неправильного refresh token", "model": IncorrectLogin}})
async def refresh_token(token: str = Body(embed=True)) -> Token:
    """Роут для обновления токена доступа пользователей"""
    token: Token = await worker.get_new_access_token(refresh_token=token)
    return token


@router.post("/logout/", tags=["Initialization"], status_code=status.HTTP_204_NO_CONTENT)
async def logout(token: str = Body(embed=True)) -> None:
    """Роут для выхода текущего пользователя из системы"""
    await worker.logout_user(refresh_token=token)
