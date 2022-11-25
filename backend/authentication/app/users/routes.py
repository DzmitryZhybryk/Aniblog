import asyncio

from datetime import timedelta
from fastapi import APIRouter, Depends, UploadFile, status
from cashews import noself_cache

from .schemas import UserOut, UserUpdate
from .dependency import user_services, RoleRequired
from ..config import database_config
from ..models import User
from ..database import cache

router = APIRouter()


@router.get("/me/",
            response_model=UserOut,
            dependencies=[Depends(RoleRequired(database_config.roles))],
            tags=["User"],
            status_code=status.HTTP_200_OK)
@noself_cache(ttl=timedelta(minutes=1))
async def current_user(user: User = Depends(user_services.get_current_user)):
    """Роут для получения информации о текущем пользователе"""
    await asyncio.sleep(5)
    return (UserOut(
        username=user.username, first_name=user.first_name, last_name=user.last_name, nickname=user.nickname,
        email=user.email, birthday=user.birthday, user_role=user.user_role.role, created_at=user.created_at
    ))


@router.put("/me/",
            response_model=UserUpdate,
            dependencies=[Depends(RoleRequired(database_config.roles))],
            tags=["User"],
            status_code=status.HTTP_200_OK)
@cache.invalidate(current_user)
async def current_user_update(update_data: UserUpdate, user: User = Depends(user_services.get_current_user)):
    """Роут для изменения данных текущего пользователя"""
    updated_user = await user_services.update_current_user(user, update_data)
    return updated_user


@router.post("/photo/",
             dependencies=[Depends(RoleRequired(database_config.roles))],
             tags=["User"],
             status_code=status.HTTP_201_CREATED)
async def upload_photo(photo: UploadFile | None = None):
    photo.filename = "123.jpg"
    content = await photo.read()
    print(photo.filename)
