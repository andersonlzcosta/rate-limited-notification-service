from fastapi import FastAPI
from app.config import settings
from app.adapters.redis_client import RedisClient

app = FastAPI(
    title="Notification Service",
    description="Rate-limited notification microservice",
    version="1.0.0"
)


@app.get("/")
async def root():
    """Root endpoint returning Hello World"""
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "notification-service"
    }


@app.get("/health/redis")
async def health_redis():
    """Health check endpoint for Redis connection"""
    redis_client = RedisClient(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT
    )
    
    try:
        is_connected = await redis_client.test_connection()
        if is_connected:
            return {
                "status": "connected",
                "service": "redis",
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT
            }
        else:
            return {
                "status": "disconnected",
                "service": "redis",
                "host": settings.REDIS_HOST,
                "port": settings.REDIS_PORT
            }
    except Exception as e:
        return {
            "status": "error",
            "service": "redis",
            "error": str(e)
        }
    finally:
        await redis_client.close()

