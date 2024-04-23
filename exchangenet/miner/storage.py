import os
import json

from redis import asyncio as aioredis
from dotenv import load_dotenv


load_dotenv()

REDIS_SERVER_HOST = os.getenv('REDIS_SERVER_HOST', 'localhost')
REDIS_SERVER_PORT = os.getenv('REDIS_SERVER_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 1)
REDIS_SERVER_PASSWORD = os.getenv('REDIS_SERVER_PASSWORD', None)

class MinerStorage():
    """
    The MinerStorage class provides functionality for miners to store `swap_id`s. 

    As a default, it uses Redis as a backend and provides methods for storing, retrieving, and managing data.
    """

    def __init__(self, account: str):
        self.redis = aioredis.Redis(host=REDIS_SERVER_HOST, port=REDIS_SERVER_PORT, db=REDIS_DB, password=REDIS_SERVER_PASSWORD, decode_responses=True)
        self.pool_name = f'miner_{account}_swaps'

    async def store_swap(self, swap_id: str, chain_name: str):
        return await self.redis.hset(self.pool_name, swap_id, chain_name)

    async def retrieve_swap(self, swap_id: str):
        return await self.redis.hget(self.pool_name, swap_id)

    async def retrieve_swaps(self):
        return await self.redis.hkeys(self.pool_name)

    async def delete_swap(self, swap_id: str):
        return await self.redis.delete(self.pool_name, swap_id)
