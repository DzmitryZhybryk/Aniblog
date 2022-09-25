from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordRequestFormStrict

from .schemas import UserRegistration, TokenData, UserBase, UserAdditionData
from .dependency import registration_user, get_current_active_user, authenticate_user, add_user_data
from .config import config

router = APIRouter()


@router.post("/registration/", response_model=TokenData)
async def registration(user: UserRegistration = Depends(registration_user)):
    return user


@router.post("/token/", response_model=TokenData)
async def login_for_access_token(user: UserBase = Depends(authenticate_user)):
    return user


@router.post("/me/", response_model=UserAdditionData)
async def me(user: UserAdditionData = Depends(add_user_data)):
    return user
