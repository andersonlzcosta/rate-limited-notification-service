"""Tests for the NotificationService."""

import pytest
import pytest_asyncio

from app.core.gateway import Gateway, MockGateway, Notification
from app.core.notification_service import NotificationService


@pytest_asyncio.fixture
async def mock_gateway() -> MockGateway:
    """Provide a fresh MockGateway instance for each test."""
    return MockGateway()


@pytest_asyncio.fixture
async def notification_service(mock_gateway: MockGateway) -> NotificationService:
    """Provide a NotificationService instance with a mock gateway."""
    return NotificationService(gateway=mock_gateway)


@pytest.mark.asyncio
async def test_notification_service_initialization(notification_service: NotificationService):
    """NotificationService should be initialized correctly with a gateway."""
    
    assert notification_service is not None
    assert notification_service.gateway is not None


@pytest.mark.asyncio
async def test_notification_service_send_success(notification_service: NotificationService, mock_gateway: MockGateway):
    """NotificationService should successfully send a notification through the gateway."""
    
    notification = Notification(
        user_id="user123",
        notification_type="status",
        message="Your order has been shipped!"
    )
    
    result = await notification_service.send(
        user_id=notification.user_id,
        notification_type=notification.notification_type,
        message=notification.message
    )
    
    # Service should indicate success
    assert result is True
    
    # Gateway should have received the notification
    assert len(mock_gateway.sent_notifications) == 1
    sent_notification = mock_gateway.sent_notifications[0]
    assert sent_notification.user_id == "user123"
    assert sent_notification.notification_type == "status"
    assert sent_notification.message == "Your order has been shipped!"


@pytest.mark.asyncio
async def test_notification_service_send_multiple_notifications(
    notification_service: NotificationService,
    mock_gateway: MockGateway
):
    """NotificationService should handle multiple notifications correctly."""
    
    await notification_service.send(
        user_id="user1",
        notification_type="status",
        message="First notification"
    )
    
    await notification_service.send(
        user_id="user2",
        notification_type="news",
        message="Second notification"
    )
    
    await notification_service.send(
        user_id="user1",
        notification_type="marketing",
        message="Third notification"
    )
    
    # All three should be sent
    assert len(mock_gateway.sent_notifications) == 3
    
    # Verify each notification
    assert mock_gateway.sent_notifications[0].user_id == "user1"
    assert mock_gateway.sent_notifications[0].notification_type == "status"
    
    assert mock_gateway.sent_notifications[1].user_id == "user2"
    assert mock_gateway.sent_notifications[1].notification_type == "news"
    
    assert mock_gateway.sent_notifications[2].user_id == "user1"
    assert mock_gateway.sent_notifications[2].notification_type == "marketing"

