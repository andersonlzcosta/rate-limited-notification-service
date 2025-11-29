from fastapi import FastAPI
from app.config import settings

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

