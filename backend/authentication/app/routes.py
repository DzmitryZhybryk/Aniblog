from fastapi import APIRouter, Depends

from .schemas import UserRegistration, TokenData
from .dependency import registration_user

router = APIRouter()


@router.post("/registration/", response_model=TokenData)
def registration(user: UserRegistration = Depends(registration_user)):
    return user
