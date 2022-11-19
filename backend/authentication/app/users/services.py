# from datetime import timedelta, datetime
# from jose import jwt, JWTError
# from dataclasses import dataclass
# from time import time
#
# from fastapi import HTTPException, status
#
# from asyncpg.exceptions import UniqueViolationError
# from orm.exceptions import NoMatch
# from sqlite3 import IntegrityError
#
# from ..exception import UnauthorizedException
# from ..models import User, Role
# from ..config import jwt_config, database_config
# from .schemas import UserRegistration, UserUpdate, UserLogin, Token, UserRegistrationResponse, TokenData
# from ..utils.email_sender import EmailSender
# from ..utils.code_verification import verification_code
# # from ..utils.password_verification import hash_password
# from ..database import redis_database
# # from ..utils.password_verification import verify_password
#
#
# @dataclass
# class ValidatedUser:
#     user: UserRegistration
#     token: Token
#
#
# class UserAuthentication:
#
#     async def send_registration_code_to_email(self, user: UserRegistration) -> UserRegistration:
#         registration_code = verification_code.get_verification_code()
#         await redis_database.set_data(key=registration_code, value=user.json())
#         email = EmailSender(recipient=user.email, verification_code=registration_code)
#         email.send_email()
#         return user
#
#     async def _get_user_data_from_redis(self, code: int) -> str:
#         user_data = await redis_database.get_data(key=code)
#         if not user_data:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный проверочный код")
#
#         return user_data
#
#     def _create_access_token(self, data: dict, expires_delta: timedelta) -> str:
#         """
#         Функция для создания токена доступа
#
#         :param data: dict с именем пользователя
#         :param expires_delta: время жизни токена
#         :return: access token
#         """
#         to_encode = data.copy()
#         expire = datetime.utcnow() + expires_delta
#
#         to_encode.update({"exp": expire})
#         encode_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.jwt_algorithm)
#         return encode_jwt
#
#     async def _save_refresh_token_to_redis(self, username: str, refresh_token: str):
#         await redis_database.set_data(key=username, value=refresh_token)
#
#     async def _generate_token_data(self, user: UserLogin | User) -> Token:
#         """
#         Функция для создания токенов доступа
#
#         :param user: pydantic model с данными пользователя
#         :return: Token pydantic схема с bearer access token
#         """
#         access_token_expires = timedelta(minutes=jwt_config.access_token_expire)
#         refresh_token_expires = timedelta(minutes=jwt_config.refresh_token_expire)
#         access_token = self._create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
#         refresh_token = self._create_access_token(data={"sub": user.username}, expires_delta=refresh_token_expires)
#         await self._save_refresh_token_to_redis(username=user.username, refresh_token=refresh_token)
#         token_schema = Token(access_token=access_token, refresh_token=refresh_token, token_type="Bearer")
#
#         return token_schema
#
#     async def _get_user_by_validation_code(self, code: int) -> UserRegistration:
#         user_data = await self._get_user_data_from_redis(code=code)
#         user = UserRegistration.parse_raw(user_data)
#         await redis_database.delete_data(key=code)
#         return user
#
#     async def validate_code(self, code: int) -> ValidatedUser:
#         user_info = await self._get_user_by_validation_code(code=code)
#         token = await self._generate_token_data(user=user_info)
#         return ValidatedUser(user=user_info, token=token)
#
#     async def authenticate(self, db_user: User, user: UserLogin) -> Token:
#         """
#         Функция для аутентификации пользователя
#         """
#         # if not verify_password(user.password, db_user.password):
#         #     raise UnauthorizedException
#
#         token_schema = await self._generate_token_data(user)
#         return token_schema
#
#     def decode_token(self, token: str) -> TokenData:
#         try:
#             payload = jwt.decode(token, jwt_config.secret_key, algorithms=[jwt_config.jwt_algorithm])
#             username: str = payload.get("sub")
#             if username is None:
#                 raise UnauthorizedException
#
#             if payload.get("exp") < int(time()):
#                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
#             return TokenData(username=username)
#         except JWTError:
#             raise UnauthorizedException
#
#
# class UserStorage:
#
#     def __init__(self):
#         self._user_model = User
#         self._role_model = Role
#
#     async def has_users(self) -> bool:
#         """
#         Функция проверяет наличие созданных пользователей в базе данных
#
#         :return: bool object. True - если хотя бы один пользователь найден и False - если нет.
#         """
#         user_count = await self._user_model.objects.first()
#         return bool(user_count)
#
#     async def has_roles(self) -> bool:
#         """
#         Функция проверяет наличие созданных ролей в базе данных
#
#         :return: bool object. True - если хотя бы одна роль найдена и False - если нет.
#         """
#         roles_count = await self._role_model.objects.first()
#         return bool(roles_count)
#
#     async def create_initial_roles(self) -> None:
#         """Функция для создания ролей пользователей в базе данных"""
#         if not await self.has_roles():
#             for role in database_config.roles:
#                 await self._role_model.objects.create(role=role)
#
#     async def create_initial_user(self) -> None:
#         """Функция для создания первого пользователя при запуске приложения"""
#         if not await self.has_roles():
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Roles not found")
#
#         if not await self.has_users():
#             # hashed_password = hash_password("admin")
#             initial_user_role = await self._role_model.objects.get(role="admin")
#             await self._user_model.objects.create(username="admin", password="123",
#                                                   user_role=initial_user_role,
#                                                   email="test@mail.ru")
#
#     async def _get_db_user_by_username(self, username: str) -> User:
#         user: User = await self._user_model.objects.get(username=username)
#         return user
#
#     async def get_user_by_username(self, username: str, raise_nomatch: bool = False) -> User | None:
#         """
#         Функция получает на вход имя пользователя, ищет его в базе данных и если находит, возвращает этого пользователя
#
#         :param username: имя пользователя которого будем искать в базе данных
#         :param raise_nomatch: если True - рейзит исключение, если пользователь не найден. Если False - возвращает None.
#             По умолчанию False
#         :return: объект класса User с данными пользователя из базы данных
#
#         """
#         try:
#             user = await self._get_db_user_by_username(username=username)
#             await user.user_role.load()
#             return user
#         except NoMatch:
#             if raise_nomatch:
#                 raise UnauthorizedException
#
#     async def get_user_by_id(self, user_id: str, raise_nomatch: bool = False) -> User:
#         try:
#             user = await self._user_model.objects.get(id=user_id)
#             return user
#         except NoMatch:
#             if raise_nomatch:
#                 raise HTTPException(status_code=404, detail="User not found")
#
#     async def check_user_exists(self, username: str):
#         db_user = await self._get_db_user_by_username(username=username)
#         if db_user:
#             raise HTTPException(status_code=status.HTTP_409_CONFLICT,
#                                 detail=f"Account with username {username} already exist")
#
#         return db_user
#
#     async def create(self, user_data: UserRegistration) -> User:
#         # hashed_password = hash_password(user_data.password)
#         try:
#             new_db_user_role = await self._role_model.objects.get(role="base_user")
#             new_db_user = await self._user_model.objects.create(username=user_data.username, password="123",
#                                                                 user_role=new_db_user_role, email=user_data.email)
#             return new_db_user
#         except (UniqueViolationError, IntegrityError) as ex:
#             raise HTTPException(
#                 status_code=status.HTTP_409_CONFLICT,
#                 detail=f"{ex}: Account already exist"
#             )
#
#     @staticmethod
#     def _is_birthday_exist(db_user: User) -> bool:
#         """
#         Функция проверяет, заполнено ли поле birthday в базе данных
#
#         :param db_user: пользователь из базы данных
#         :return: True, если поле birthday заполнено в базе данных и False, если нет
#         """
#         if db_user.birthday:
#             return True
#
#     async def update(self, db_user: User, user_info: UserUpdate) -> User:
#         """
#         Функция обновляет данные текущего пользователя в базе данных
#
#         :param user_info: UserUpdate pydantic схема с данными, которые надо обновить в базе данных
#         :return: объект класса User с обновленными данными пользователя из базы данных
#         """
#         try:
#             if user_info.birthday and self._is_birthday_exist(db_user):
#                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                                     detail="День рождения можно поменять один раз!")
#
#             await db_user.update(username=user_info.username, first_name=user_info.first_name,
#                                  last_name=user_info.last_name, birthday=user_info.birthday)
#             return db_user
#         except NoMatch:
#             raise UnauthorizedException
#
#
# class UserServices:
#
#     def __init__(self):
#         self._authentication = UserAuthentication()
#         self._storage = UserStorage()
#
#     async def login(self, user: UserLogin) -> Token:
#         db_user = await self._storage.get_user_by_username(user.username, raise_nomatch=True)
#         token_schema = await self._authentication.authenticate(db_user, user)
#         return token_schema
#
#     async def refresh_token(self):
#         pass
#
#     async def validate_user_registration(self, code: int) -> Token:
#         validated_user = await self._authentication.validate_code(code)
#         await self._storage.create(validated_user.user)
#         return validated_user.token
#
#     async def registrate(self, user: UserRegistration) -> UserRegistrationResponse:
#         await self._authentication.send_registration_code_to_email(user)
#         user_response_data = UserRegistrationResponse(username=user.username, email=user.email)
#         return user_response_data
#
#     async def update_current_user(self, db_user: User, user_info: UserUpdate) -> UserUpdate:
#         updated_user = await self._storage.update(db_user, user_info)
#         updated_user_schema = UserUpdate.from_orm(updated_user)
#         return updated_user_schema
#
#
# user_services = UserServices()
