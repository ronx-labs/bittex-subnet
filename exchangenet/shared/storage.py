import os
import json

from redis import asyncio as aioredis
from dotenv import load_dotenv


load_dotenv()

REDIS_SERVER_HOST = os.getenv('REDIS_SERVER_HOST', 'localhost')
REDIS_SERVER_PORT = os.getenv('REDIS_SERVER_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 1)
REDIS_SERVER_PASSWORD = os.getenv('REDIS_SERVER_PASSWORD', None)

class Storage():
    """
    The SwapPool class provides functionality for both miners and validators to store `swap_id`s. 

    As a default, it uses Redis as a backend for storage and provides methods for storing, retrieving, and managing data.
    """

    def __init__(self, host: str = REDIS_SERVER_HOST, port: int = REDIS_SERVER_PORT, db: int = REDIS_DB, password: str = REDIS_SERVER_PASSWORD):
        self.redis = aioredis.Redis(host=host, port=port, db=db, password=password, decode_responses=True)

    async def store_data(self, name: str, key: str, value: any):
        return await self.redis.hset(name, key, value)

    async def retrieve_data(self, name: str, key: str):
        return await self.redis.hget(name, key)

    async def delete_data(self, name: str, key: str):
        return await self.redis.hdel(name, key)

    async def exists_data(self, name: str, key: str) -> bool:
        return await self.redis.hexists(name, key)

    async def delete_name(self, name: str):
        return await self.redis.delete(name)

    async def get_all_data(self, name: str):
        return await self.redis.hkeys(name)

    async def clear_redis(self):
        await self.redis.flushdb()

    async def close(self):
        self.redis.close()
        await self.redis.wait_closed()