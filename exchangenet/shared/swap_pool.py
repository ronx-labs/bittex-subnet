from redis import asyncio as aioredis
import json

class SwapPool():
    """
    The SwapPool class provides functionality for both miners and validators to store `swap_id`s. 

    As a default, it uses Redis as a backend for storage and provides methods for storing, retrieving, and managing data.
    """

    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0, password: str = None):
        self.redis = aioredis.Redis(host=host, port=port, db=db, password=password)

    async def store(self, key: str, value):
        serialized_data = json.dumps(value) # Serialize the data before storing it.
        await self.redis.set(key, serialized_data)

    async def retrieve(self, key: str):
        serialized_data = await self.redis.get(key)
        # Deserialize the data before returning it.
        if serialized_data:
            return json.loads(serialized_data)
        else:
            return None

    async def retrieve_all_swaps(self, pattern: str = '*'):
        keys = await self.redis.keys(pattern)
        return keys

    async def delete(self, key: str):
        await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        return await self.redis.exists(key)

    async def clear(self):
        await self.redis.flushdb()

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()