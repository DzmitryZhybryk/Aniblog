import asyncio

import aioredis


async def main():
    redis = aioredis.from_url("redis://localhost", username="admin", password="admin", db=0)
    await redis.set("my-key", "value")
    value = await redis.get("my-key")
    await redis.delete("my-key")
    print(value)
    await redis.close()


if __name__ == "__main__":
    asyncio.run(main())
