from __future__ import annotations

from app.core.gateway import Gateway, Notification


class NotificationService:
    """Service for sending notifications through a gateway."""

    def __init__(self, gateway: Gateway) -> None:
        self.gateway = gateway

    async def send(
        self,
        user_id: str,
        notification_type: str,
        message: str,
    ) -> bool:
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            message=message,
        )
        
        return await self.gateway.send(notification)
