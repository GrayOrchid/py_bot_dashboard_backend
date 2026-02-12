import redis.asyncio as redis


class StateService:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379/0", decode_responses=True)

    async def save_state(self, state: str, expires_in: int = 900):
        await self.redis.set(name=f"oauth_state:{state}", value="1", ex=expires_in)
        print(f"DEBUG: State {state} saved to Redis")

    async def validate_state(self, state: str) -> bool:
        key = f"oauth_state:{state}"
        exists = await self.redis.exists(key)

        if exists:
            await self.redis.delete(key)
            print(f"DEBUG: State {state} is valid")
            return True

        print(f"DEBUG: State {state} not found or expired in Redis")
        return False