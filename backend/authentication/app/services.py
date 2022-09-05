from .models import User


async def has_db_user() -> bool:
    user_count = await User.objects.first()
    return bool(user_count)


async def create_initial_user():
    initial_user = await User.objects.create(username="admin", password="admin")
