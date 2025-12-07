import threading
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.adapters.redis_client import RedisClient
from app.core.consumer import NotificationConsumer
from app.core.notification_service import NotificationService
from app.core.gateway import MockGateway

logger = logging.getLogger(__name__)

consumer_thread: threading.Thread = None
consumer: NotificationConsumer = None

def run_consumer():
    """Run the consumer in a separate thread."""
    global consumer
    try:
        logger.info("Starting RabbitMQ consumer...")
        gateway = MockGateway()
        service = NotificationService(gateway)
        consumer = NotificationConsumer(service=service, queue_name="notifications")
        consumer.start_consuming()
    except Exception as e:
        logger.error(f"Error in consumer thread: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global consumer_thread
    logger.info("Starting up notification service...")
    
    consumer_thread = threading.Thread(target=run_consumer, daemon=True)
    consumer_thread.start()
    logger.info("RabbitMQ consumer thread started")
    
    yield
    
    logger.info("Shutting down notification service...")
    if consumer:
        consumer.stop_consuming()
    logger.info("RabbitMQ consumer stopped")


app = FastAPI(
    title="Notification Service",
    description="Rate-limited notification microservice",
    version="1.0.0",
    lifespan=lifespan
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

