#!/usr/bin/env python3
"""Helper script to publish test messages to RabbitMQ."""
import json
import pika
import sys
from app.config import settings


def publish_message(user_id: str, notification_type: str, message: str):
    """Publish a notification message to RabbitMQ."""
    # Connect to RabbitMQ
    credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        credentials=credentials
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # Declare exchange (same as consumer)
    channel.exchange_declare(exchange='notifications', exchange_type='direct', durable=True)
    
    # Create message payload
    payload = {
        "user_id": user_id,
        "type": notification_type,
        "message": message
    }
    
    # Publish message
    channel.basic_publish(
        exchange='notifications',
        routing_key='notification.send',
        body=json.dumps(payload),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )
    
    print(f"✓ Message published successfully!")
    print(f"  User ID: {user_id}")
    print(f"  Type: {notification_type}")
    print(f"  Message: {message}")
    
    connection.close()


if __name__ == "__main__":
    # Default values
    user_id = sys.argv[1] if len(sys.argv) > 1 else "user1"
    notification_type = sys.argv[2] if len(sys.argv) > 2 else "news"
    message = sys.argv[3] if len(sys.argv) > 3 else "Test notification"
    
    try:
        publish_message(user_id, notification_type, message)
    except Exception as e:
        print(f"✗ Error publishing message: {e}")
        sys.exit(1)

