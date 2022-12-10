from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from ..exception import UnauthorizedException
from ..responses import IncorrectLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Password:

    def __init__(self, password: str):
        self._password = password

    def hash_password(self) -> str:
        return pwd_context.hash(self._password)

    def verify_password(self, hashed_password: str) -> bool:
        try:
            is_verify = pwd_context.verify(self._password, hashed_password)
            if not is_verify:
                raise UnauthorizedException(detail=IncorrectLogin)
            return is_verify
        except UnknownHashError:
            raise UnauthorizedException(detail=IncorrectLogin)
