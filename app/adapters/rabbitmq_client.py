"""RabbitMQ client adapter for connection and queue operations."""
import pika
import pika.exceptions
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class RabbitMQClient:
    """RabbitMQ client wrapper for connection and queue management."""
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 5672,
        username: str = "admin",
        password: str = "admin",
        virtual_host: str = "/"
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.virtual_host = virtual_host
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None
    
    def connect(self) -> pika.BlockingConnection:
        if self._connection is None or self._connection.is_closed:
            logger.info(
                f"Connecting to RabbitMQ at {self.host}:{self.port} "
                f"with user: {self.username}, virtual_host: {self.virtual_host}"
            )
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials
            )
            try:
                self._connection = pika.BlockingConnection(parameters)
                logger.info(f"Successfully connected to RabbitMQ at {self.host}:{self.port}")
            except pika.exceptions.ProbableAuthenticationError as e:
                logger.error(
                    f"Authentication failed for user '{self.username}' at {self.host}:{self.port}. "
                    f"Error: {e}"
                )
                raise
            except Exception as e:
                logger.error(f"Failed to connect to RabbitMQ at {self.host}:{self.port}. Error: {e}")
                raise
        
        return self._connection
    
    def get_channel(self) -> pika.channel.Channel:
        if self._channel is None or self._channel.is_closed:
            connection = self.connect()
            self._channel = connection.channel()
            logger.info("RabbitMQ channel created")
        
        return self._channel
    
    def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False
    ) -> None:
        channel = self.get_channel()
        channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete
        )
        logger.info(f"Queue '{queue_name}' declared")
    
    def declare_exchange(
        self,
        exchange_name: str,
        exchange_type: str = "direct",
        durable: bool = True
    ) -> None:
        channel = self.get_channel()
        channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )
        logger.info(f"Exchange '{exchange_name}' declared as type '{exchange_type}'")
    
    def bind_queue(
        self,
        queue_name: str,
        exchange_name: str,
        routing_key: str
    ) -> None:
        channel = self.get_channel()
        channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        logger.info(f"Queue '{queue_name}' bound to exchange '{exchange_name}' with routing key '{routing_key}'")
    
    def close(self) -> None:
        if self._channel and not self._channel.is_closed:
            self._channel.close()
            self._channel = None
        
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            self._connection = None
        
        logger.info("RabbitMQ connection closed")

