from fastapi import APIRouter, Depends

from .schemas import RegUser, RegUserOut
from .dependency import registration

router = APIRouter()


@router.post("/registration/", response_model=RegUserOut)
def registration(user: RegUser = Depends(registration)):
    return RegUserOut(username=user.username, token="some_token")
