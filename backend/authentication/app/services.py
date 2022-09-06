from passlib.context import CryptContext

from .models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def has_db_user() -> bool:
    user_count = await User.objects.first()
    return bool(user_count)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def create_initial_user():
    hashed_password = get_password_hash("admin")
    await User.objects.create(username="admin", password=hashed_password, role="admin")
