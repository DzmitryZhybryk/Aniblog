"""
Модуль хранит в себе InitializationService класс, который служит для генерации токенов доступа,
а так же для регистрации и аутентификации пользователей

"""
from .services import UserStorage, UserInitialization
from .schemas import UserRegistration, UserLogin, Token, UserRegistrationResponse


class InitializationServices:
    """
    Класс используется для управлением регистрацией, аутентификацией и авторизацией пользователей

    """

    def __init__(self):
        self._initialization = UserInitialization()
        self._storage = UserStorage()

    async def user_registration(self, user: UserRegistration) -> UserRegistrationResponse:
        """
        Метод для начала регистрации новых пользователей. Результатом его работы является отправка кода
        подвтерждения регистрации, на электронную почту пользователей, которые пытаются зарегистрироваться.

        Args:
            user: pydantic схема c данными пользователя, указанными при регистрации

        Returns:
            UserRegistrationResponse pydantic схему с данными пользователя, который пытается зарегистрироваться

        """
        await self._initialization.send_registration_code_to_email(user=user)
        user_response_data = UserRegistrationResponse(username=user.username, email=user.email)
        return user_response_data

    async def validate_user_registration(self, code: str) -> Token:
        """
        Метод для подтверждения регистрации нового пользователя. Пытается найти полученный код в базе данных
        redis. Если такой код там найден - отправляет запроc в PostgreSQL базу данных для создания в ней
        нового пользователя. После этого генерирует и возвращает токены доступа для этого пользователя.
        Полученный код будет удалён из redis.

        Args:
            code: проверочный код, который был отправлен новому пользователю на электронный адрес, для подвтерждения регистраци

        Returns:
            Token pydantic схему с токенами доступа для авторизации пользователя

        """
        validated_user = await self._initialization.validate_code(code=code)
        new_db_user = await self._storage.create(user_data=validated_user)
        tokens: Token = await self._initialization.generate_token_data(user=new_db_user)
        return tokens

    async def login(self, user: UserLogin) -> Token:
        """
        Метод используется для аутентификации пользователей. Принимает на вход UserLogin pydantic схему с
        username и password пользователя. Далее по полученному username формирует запрос в PostgreSQL,
        с целью выяснить, существует такой пользователь, или нет. Если такой пользователь найден, производит
        проверку введённого password и password из базы данных на соответствие. В случае успешной
        аутентификации - возвращает токены, для получения доступа к ресурсам приложения

        Args:
            user: UserLogin pydantic схема с данными пользователя, который пытается аутентифицироваться

        Returns:
            Token pydantic схему с токенами доступа для авторизации пользователя

        """
        db_user = await self._storage.get_user_by_username(username=user.username, raise_nomatch=True)
        token_schema = await self._initialization.authenticate(db_user=db_user, user=user)
        return token_schema

    async def get_new_access_token(self, refresh_token: str) -> Token:
        """
        Метод используется для генерации нового access_token на основе refresh_token. При получении
        refresh_token - пытается найти его в базе данных redis. Если это удаётся, по этому же refresh_token
        запрашивается информация из redis для генерации нового access_token.

        Args:
            refresh_token: текущий refresh_token пользователя

        Returns:
            Token pydantic схему с токенами доступа для авторизации пользователя

        """
        new_access_token = await self._initialization.compare_refresh_token(current_refresh_token=refresh_token)
        token_schema: Token = Token(access_token=new_access_token, refresh_token=refresh_token)
        return token_schema


worker = InitializationServices()
