from redis.asyncio import Redis, ConnectionPool
from contextlib import asynccontextmanager
from core.config import settings

REDIS_URL = settings.REDIS_URL

pool = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
)

redis_client = Redis(connection_pool=pool)

@asynccontextmanager
async def redis_lifespan():
    try:
        await redis_client.ping()
        print("Redis подключён")
        yield
    finally:
        await redis_client.aclose()
        print("Redis отключён")