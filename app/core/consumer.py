"""RabbitMQ consumer for processing notification messages."""
import json
import logging
from typing import Optional
import pika
from app.core.notification_service import NotificationService
from app.adapters.rabbitmq_client import RabbitMQClient

logger = logging.getLogger(__name__)


class NotificationConsumer:    
    def __init__(
        self,
        service: NotificationService,
        queue_name: str = "notifications",
        rabbitmq_client: Optional[RabbitMQClient] = None
    ):
        self.service = service
        self.queue_name = queue_name
        self.rabbitmq_client = rabbitmq_client
        self._channel: Optional[pika.channel.Channel] = None
        self._connection: Optional[pika.BlockingConnection] = None
    
    def _get_rabbitmq_client(self) -> RabbitMQClient:
        if self.rabbitmq_client is None:
            from app.config import settings
            logger.info(
                f"Connecting to RabbitMQ at {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT} "
                f"with user: {settings.RABBITMQ_USER}"
            )
            self.rabbitmq_client = RabbitMQClient(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                username=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS
            )
        return self.rabbitmq_client
    
    async def _process_message(self, message_body: str) -> None:
        try:
            data = json.loads(message_body)
          
            user_id = data["user_id"]
            notification_type = data["type"]
            message = data["message"]
            
            result = await self.service.send(
                user_id=user_id,
                notification_type=notification_type,
                message=message
            )
            
            if result:
                logger.info(
                    f"Notification sent successfully: user_id={user_id}, "
                    f"type={notification_type}"
                )
            else:
                logger.warning(
                    f"Notification sending failed: user_id={user_id}, "
                    f"type={notification_type}"
                )
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in message: {e}")
            raise
        
        except KeyError as e:
            logger.error(f"Missing required field in message: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
    
    def _on_message(
        self,
        channel: pika.channel.Channel,
        method: pika.spec.Basic.Deliver,
        properties: pika.spec.BasicProperties,
        body: bytes
    ) -> None:
    
        try:
            message_body = body.decode('utf-8')
            logger.info(f"Received message: {message_body}")
            
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_closed():
                    asyncio.run(self._process_message(message_body))
                else:
                    loop.run_until_complete(self._process_message(message_body))
            except RuntimeError:
                asyncio.run(self._process_message(message_body))
            
            channel.basic_ack(delivery_tag=method.delivery_tag)
        
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            
            channel.basic_nack(
                delivery_tag=method.delivery_tag,
                requeue=False
            )
    
    def start_consuming(self) -> None:
        
        client = self._get_rabbitmq_client()
        
        exchange_name = "notifications"
        client.declare_exchange(exchange_name, exchange_type="direct")
        
        client.declare_queue(self.queue_name)
    
        routing_key = "notification.send"
        client.bind_queue(self.queue_name, exchange_name, routing_key)
        
        self._channel = client.get_channel()
        self._connection = client._connection
        
        self._channel.basic_qos(prefetch_count=1)
        
        self._channel.basic_consume(
            queue=self.queue_name,
            on_message_callback=self._on_message
        )
        
        logger.info(
            f"Started consuming from queue '{self.queue_name}' "
            f"bound to exchange 'notifications' with routing key 'notification.send'"
        )
        
        try:
            self._channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.stop_consuming()
    
    def stop_consuming(self) -> None:
        if self._channel and not self._channel.is_closed:
            self._channel.stop_consuming()
            logger.info("Stopped consuming messages")
        
        if self.rabbitmq_client:
            self.rabbitmq_client.close()

