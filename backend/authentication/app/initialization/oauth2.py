from .services import UserStorage, UserInitialization
from .schemas import UserRegistration, UserLogin, Token, UserRegistrationResponse


class InitializationServices:

    def __init__(self):
        self._initialization = UserInitialization()
        self._storage = UserStorage()

    async def user_registration(self, user: UserRegistration) -> UserRegistrationResponse:
        await self._initialization.send_registration_code_to_email(user=user)
        user_response_data = UserRegistrationResponse(username=user.username, email=user.email)
        return user_response_data

    async def validate_user_registration(self, code: str) -> Token:
        validated_user = await self._initialization.validate_code(code=code)
        db_user = await self._storage.create(validated_user)
        tokens: Token = await self._initialization.generate_token_data(user=db_user)
        return tokens

    async def login(self, user: UserLogin) -> Token:
        db_user = await self._storage.get_user_by_username(user.username, raise_nomatch=True)
        token_schema = await self._initialization.authenticate(db_user=db_user, user=user)
        return token_schema

    async def get_new_access_token(self, current_refresh_token: str) -> Token:
        new_access_token = await self._initialization.compare_refresh_token(current_refresh_token=current_refresh_token)
        token_schema: Token = Token(access_token=new_access_token, refresh_token=current_refresh_token)
        return token_schema


worker = InitializationServices()
