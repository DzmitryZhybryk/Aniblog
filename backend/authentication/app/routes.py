from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordRequestFormStrict

from .schemas import UserRegistration, TokenData, UserBase
from .dependency import registration_user, get_current_active_user, authenticate_user
from .config import config

router = APIRouter()


@router.post("/registration/", response_model=TokenData)
async def registration(user: UserRegistration = Depends(registration_user)):
    return user


@router.post("/token/", response_model=TokenData)
async def login_for_access_token(user: UserBase = Depends(authenticate_user)):
    return user
