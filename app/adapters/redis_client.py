"""Redis client adapter for connection and operations"""
import redis.asyncio as aioredis
from typing import Optional


class RedisClient:
    """Redis client wrapper for async operations"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """
        Initialize Redis client
        
        Args:
            host: Redis host address
            port: Redis port
            db: Redis database number
        """
        self.host = host
        self.port = port
        self.db = db
        self._client: Optional[aioredis.Redis] = None
    
    async def _get_client(self) -> aioredis.Redis:
        """Get or create Redis client connection"""
        if self._client is None:
            self._client = aioredis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
        return self._client
    
    async def test_connection(self) -> bool:
        """
        Test Redis connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            client = await self._get_client()
            await client.ping()
            return True
        except Exception:
            return False
    
    async def ping(self) -> bool:
        """
        Ping Redis server
        
        Returns:
            True if ping is successful
        """
        client = await self._get_client()
        result = await client.ping()
        return result is True
    
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis
        
        Args:
            key: Redis key
            value: Value to store
            expire: Optional expiration time in seconds
            
        Returns:
            True if successful
        """
        client = await self._get_client()
        if expire:
            return await client.setex(key, expire, value)
        return await client.set(key, value)
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis by key
        
        Args:
            key: Redis key
            
        Returns:
            Value if exists, None otherwise
        """
        client = await self._get_client()
        return await client.get(key)
    
    async def delete(self, key: str) -> int:
        """
        Delete a key from Redis
        
        Args:
            key: Redis key
            
        Returns:
            Number of keys deleted
        """
        client = await self._get_client()
        return await client.delete(key)
    
    async def close(self):
        """Close Redis connection"""
        if self._client:
            await self._client.close()
            self._client = None

