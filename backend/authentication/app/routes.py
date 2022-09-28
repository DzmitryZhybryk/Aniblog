from fastapi import APIRouter, Depends

from .schemas import Token, UserOut
from .dependency import registration_user, get_current_active_user, authenticate_user

router = APIRouter()


@router.post("/registration/", response_model=Token)
async def registration(token: Token = Depends(registration_user)):
    return token


@router.post("/token/", response_model=Token)
async def login_for_access_token(token: Token = Depends(authenticate_user)):
    return token


@router.get("/user/", response_model=UserOut)
async def get_user(current_user: UserOut = Depends(get_current_active_user)):
    return current_user
