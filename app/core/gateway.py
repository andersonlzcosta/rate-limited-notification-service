"""Gateway abstractions for sending notifications.

This module defines an abstract `Gateway` interface and concrete
implementations used by the notification service.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Notification:
    """Simple value object representing a notification request."""

    user_id: str
    notification_type: str
    message: str


class Gateway(ABC):
    """Abstract base class for notification gateways."""

    @abstractmethod
    async def send(self, notification: Notification) -> bool:
        """Send a notification.

        Returns:
            True if sending was successful, False otherwise.
        """


class MockGateway(Gateway):
    """Mock gateway implementation used for testing."""

    def __init__(self) -> None:
        self._sent_notifications: List[Notification] = []

    @property
    def sent_notifications(self) -> List[Notification]:
        """Return a copy of sent notifications for inspection in tests."""
        return list(self._sent_notifications)

    async def send(self, notification: Notification) -> bool:
        self._sent_notifications.append(notification)
        return True


class EmailGateway(Gateway):
    """Real email gateway stub."""

    async def send(self, notification: Notification) -> bool:
        # TODO: Implement real email sending logic.
        raise NotImplementedError("EmailGateway.send is not implemented yet")


