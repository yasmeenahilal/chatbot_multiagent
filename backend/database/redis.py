import redis.asyncio as aioredis
from config.settings import Config

# Redis configuration
JTI_EXPIRY = 3000  # Expiry time for JTI in seconds

# Create a Redis connection pool
token_blocklist = aioredis.Redis(
    host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0
)


async def add_jti_to_blocklist(jti: str) -> None:
    """
    Add a JTI (JWT ID) to the Redis blocklist.
    """
    try:
        await token_blocklist.set(name=jti, value="blocked", ex=JTI_EXPIRY)
    except Exception as e:
        print(f"Error adding JTI to blocklist: {e}")
        raise


async def token_in_blocklist(jti: str) -> bool:
    """
    Check if a JTI (JWT ID) is in the Redis blocklist.
    """
    try:
        jti_value = await token_blocklist.get(jti)
        return jti_value is not None  # True if JTI exists, False otherwise
    except Exception as e:
        print(f"Error checking JTI in blocklist: {e}")
        return False  # Assume token is not blocked if there's an error


async def close_redis_connection():
    """
    Close the Redis connection.
    """
    await token_blocklist.close()