from datetime import datetime, timedelta
from time import time

from fastapi import status
from fastapi.exceptions import HTTPException
from jose import jwt, JWTError

from ..config import jwt_config
from ..exception import UnauthorizedException


class TokenWorker:

    async def create_access_token(self, username: str, role: str):
        access_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.access_token_expire)
        access_token = self._create_token(
            data={"sub": username, "role": role, "exp": access_token_expires})
        return access_token

    async def create_refresh_token(self):
        refresh_token_expires = datetime.utcnow() + timedelta(minutes=jwt_config.refresh_token_expire)
        refresh_token = self._create_token(data={"exp": refresh_token_expires})
        return refresh_token

    @staticmethod
    def _create_token(data: dict) -> str:
        """
        Метод создает токен для пользователя.

        Args:
            data: словарь с данными пользователя, которые будут закодированы в токене.

        Returns:
            токен пользователя.

        """
        to_encode = data.copy()
        encode_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.jwt_algorithm)
        return encode_jwt

    @staticmethod
    def decode_refresh_token(refresh_token: str) -> str:
        """
        Метод декодирует refresh_token пользователя. Проверяет, что токен не истек.

        Args:
            refresh_token: refresh_token пользователя.

        Returns:
            refresh_token пользователя.

        Exceptions:
            UnauthorizedException: Eckb если токен истек.

        """
        try:
            payload = jwt.decode(refresh_token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
            if payload.get("exp") < int(time()):
                raise UnauthorizedException

            return refresh_token
        except JWTError:
            raise UnauthorizedException

    @staticmethod
    def decode_token(token: str) -> str:
        try:
            payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
            username: str = payload.get("sub")
            if username is None:
                raise UnauthorizedException

            if payload.get("exp") < int(time()):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

            return username
        except JWTError:
            raise UnauthorizedException


token_worker = TokenWorker()
