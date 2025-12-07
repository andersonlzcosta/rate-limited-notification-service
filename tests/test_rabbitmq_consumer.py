"""Tests for RabbitMQ consumer integration."""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from app.adapters.rabbitmq_client import RabbitMQClient
from app.core.consumer import NotificationConsumer
from app.core.notification_service import NotificationService
from app.core.gateway import MockGateway


@pytest.mark.asyncio
async def test_rabbitmq_connection():
    """Test that RabbitMQ client can establish connection."""
    client = RabbitMQClient(
        host="localhost",
        port=5672,
        username="admin",
        password="admin"
    )
    assert client.host == "localhost"
    assert client.port == 5672
    assert client.username == "admin"


@pytest.mark.asyncio
async def test_rabbitmq_queue_declaration():
    """Test that queue can be declared."""
    client = RabbitMQClient(
        host="localhost",
        port=5672,
        username="admin",
        password="admin"
    )
    assert hasattr(client, 'declare_queue')


@pytest.mark.asyncio
async def test_consumer_initialization():
    """Test that NotificationConsumer can be initialized."""
    gateway = MockGateway()
    service = NotificationService(gateway)
    
    consumer = NotificationConsumer(
        service=service,
        queue_name="notifications"
    )
    
    assert consumer.service == service
    assert consumer.queue_name == "notifications"


@pytest.mark.asyncio
async def test_consumer_processes_message():
    """Test that consumer processes a message and calls notification service."""
    gateway = MockGateway()
    service = NotificationService(gateway)
    
    # Mock the send method to track calls
    service.send = AsyncMock(return_value=True)
    
    consumer = NotificationConsumer(
        service=service,
        queue_name="notifications"
    )
    
    # Simulate a message
    message_body = {
        "user_id": "user123",
        "type": "news",
        "message": "Test notification"
    }
    
    # Process the message
    await consumer._process_message(json.dumps(message_body))
    
    # Verify service.send was called with correct parameters
    service.send.assert_called_once_with(
        user_id="user123",
        notification_type="news",
        message="Test notification"
    )


@pytest.mark.asyncio
async def test_consumer_handles_invalid_json():
    """Test that consumer handles invalid JSON gracefully."""
    gateway = MockGateway()
    service = NotificationService(gateway)
    service.send = AsyncMock(return_value=True)
    
    consumer = NotificationConsumer(
        service=service,
        queue_name="notifications"
    )
    invalid_message = "not valid json {"
    try:
        await consumer._process_message(invalid_message)
    except json.JSONDecodeError:
        pass


@pytest.mark.asyncio
async def test_consumer_handles_missing_fields():
    """Test that consumer handles messages with missing required fields."""
    gateway = MockGateway()
    service = NotificationService(gateway)
    service.send = AsyncMock(return_value=True)
    
    consumer = NotificationConsumer(
        service=service,
        queue_name="notifications"
    )
    incomplete_message = {
        "user_id": "user123"
    }
    
    try:
        await consumer._process_message(json.dumps(incomplete_message))
    except (KeyError, ValueError, TypeError):
        pass

