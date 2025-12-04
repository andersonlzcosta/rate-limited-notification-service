"""Tests for the notification Gateway abstractions."""

import pytest
import pytest_asyncio

from app.core.gateway import Gateway, MockGateway, EmailGateway, Notification


@pytest_asyncio.fixture
async def mock_gateway() -> MockGateway:
    """Provide a fresh MockGateway instance for each test."""

    return MockGateway()


@pytest.mark.asyncio
async def test_mock_gateway_implements_gateway_interface(mock_gateway: MockGateway):
    """MockGateway should behave as a concrete implementation of Gateway."""

    assert isinstance(mock_gateway, Gateway)

    notification = Notification(
        user_id="user1",
        notification_type="status",
        message="Test message",
    )

    result = await mock_gateway.send(notification)

    assert result is True
    assert len(mock_gateway.sent_notifications) == 1
    assert mock_gateway.sent_notifications[0] == notification


@pytest.mark.asyncio
async def test_mock_gateway_records_multiple_notifications(mock_gateway: MockGateway):
    """MockGateway should record all sent notifications in order."""

    n1 = Notification(user_id="user1", notification_type="status", message="One")
    n2 = Notification(user_id="user2", notification_type="news", message="Two")

    await mock_gateway.send(n1)
    await mock_gateway.send(n2)

    history = mock_gateway.sent_notifications
    assert len(history) == 2
    assert history[0] == n1
    assert history[1] == n2


def test_email_gateway_is_a_gateway_but_not_implemented_yet():
    """EmailGateway should be a Gateway, but sending is not yet implemented."""

    gateway: Gateway = EmailGateway()
    assert isinstance(gateway, Gateway)