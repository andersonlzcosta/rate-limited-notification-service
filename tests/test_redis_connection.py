"""Tests for Redis connection and adapter"""
import pytest
import pytest_asyncio
from app.adapters.redis_client import RedisClient
from app.config import settings


@pytest_asyncio.fixture
async def redis_client():
    """Fixture providing a Redis client instance"""
    client = RedisClient(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_redis_connection(redis_client):
    """Test that Redis client can establish a connection"""
    is_connected = await redis_client.test_connection()
    assert is_connected is True, "Redis connection should be successful"


@pytest.mark.asyncio
async def test_redis_ping(redis_client):
    """Test that Redis client can ping the server"""
    result = await redis_client.ping()
    assert result is True, "Redis ping should return True"


@pytest.mark.asyncio
async def test_redis_client_can_set_and_get(redis_client):
    """Test basic Redis operations: set and get"""
    test_key = "test:connection"
    test_value = "test_value"
    
    await redis_client.set(test_key, test_value, expire=10)
    retrieved_value = await redis_client.get(test_key)
    
    assert retrieved_value == test_value, "Retrieved value should match set value"
    
    # Cleanup
    await redis_client.delete(test_key)

