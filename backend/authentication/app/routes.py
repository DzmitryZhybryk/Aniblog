from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordRequestFormStrict

from .schemas import UserRegistration, TokenData, Token, UserBase, UserOut, UserOut
from .dependency import registration_user, get_current_active_user, authenticate_user
from .config import config

router = APIRouter()


@router.post("/registration/", response_model=Token)
async def registration(token: Token = Depends(registration_user)):
    return token


@router.post("/token/", response_model=Token)
async def login_for_access_token(token: Token = Depends(authenticate_user)):
    return token


@router.get("/me/", response_model=UserOut)
async def me(current_user: UserOut = Depends(get_current_active_user)):
    return current_user
#
#
# @router.post("/me/", response_model=UserAdditionData)
# async def me(user: UserAdditionData = Depends(add_user_data)):
#     return user
