from datetime import timedelta

from fastapi import APIRouter, Depends, UploadFile, status

from .dependency import worker, RoleRequired
from .schemas import UserOut, UserUpdate, PasswordUpdate
from ..config import database_config
from ..database import cache_router
from ..models import User
from ..responses import NotAuthentication

router = APIRouter()


@router.get("/me/",
            response_model=UserOut,
            dependencies=[Depends(RoleRequired(database_config.roles))],
            tags=["User"],
            status_code=status.HTTP_200_OK,
            responses={200: {"description": "Операция выполнена успешно", "model": UserOut},
                       403: {"description": "Попытка получения доступа без аутентификации",
                             "model": NotAuthentication}})
@cache_router(ttl=timedelta(minutes=1))
async def current_user(user: User = Depends(worker.get_current_user)):
    """Роут для получения информации о текущем пользователе"""
    return (UserOut(
        username=user.username, first_name=user.first_name, last_name=user.last_name, nickname=user.nickname,
        email=user.email, birthday=user.birthday, user_role=user.user_role.role, created_at=user.created_at
    ))


@router.put("/me/",
            response_model=UserUpdate,
            dependencies=[Depends(RoleRequired(database_config.roles))],
            tags=["User"],
            status_code=status.HTTP_200_OK,
            responses={200: {"description": "Операция выполнена успешно", "model": UserUpdate},
                       403: {"description": "Попытка получения доступа без аутентификации",
                             "model": NotAuthentication}})
@cache_router.invalidate(current_user)
async def current_user_update(update_data: UserUpdate, user: User = Depends(worker.get_current_user)):
    """Роут для изменения данных текущего пользователя"""
    updated_user = await worker.update_current_user(user, update_data)
    return updated_user


@router.post("/me/password/",
             dependencies=[Depends(RoleRequired(database_config.roles))],
             tags=["User"],
             status_code=status.HTTP_204_NO_CONTENT,
             responses={204: {"description": "Операция выполнена успешно"},
                        403: {"description": "Попытка получения доступа без аутентификации",
                              "model": NotAuthentication}})
async def current_user_update_password(update_data: PasswordUpdate, user: User = Depends(worker.get_current_user)):
    await worker.set_new_password(update_data=update_data, user=user)


# @router.get("/ping")
# async def pong():
#     # some async operation could happen here
#     # example: `notes = await get_all_notes()`
#     return {"ping": "pong!"}
#
#
# @router.post("/photo/",
#              dependencies=[Depends(RoleRequired(database_config.roles))],
#              tags=["User"],
#              status_code=status.HTTP_201_CREATED)
# async def upload_photo(photo: UploadFile | None = None):
#     photo.filename = "123.jpg"
#     content = await photo.read()
#     print(photo.filename)
