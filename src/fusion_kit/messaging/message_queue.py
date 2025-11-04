"""
Redis-based message queue for inter-agent communication.

Implements pub/sub messaging with message persistence tracking.
"""

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class MessageQueue:
    """
    Redis-based message queue with pub/sub support.

    Handles publishing and subscribing to inter-agent messages
    with support for pattern subscriptions and message tracking.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize message queue.

        Args:
            redis_url: Redis connection URL (default: localhost:6379)
        """
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None

    async def connect(self) -> None:
        """
        Establish connection to Redis.

        Raises:
            redis.ConnectionError: If Redis is not available
        """
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
            # Test connection
            await self.redis_client.ping()
            logger.info(f"Connected to Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Redis")

    async def publish(self, topic: str, message: Dict[str, Any]) -> int:
        """
        Publish a message to a topic.

        Args:
            topic: Redis topic/channel name
            message: Message dictionary to publish

        Returns:
            Number of subscribers that received the message

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            message_json = json.dumps(message)
            subscribers_count = await self.redis_client.publish(topic, message_json)
            logger.debug(f"Published message to topic '{topic}': {subscribers_count} subscribers")
            return subscribers_count
        except Exception as e:
            logger.error(f"Failed to publish message to topic '{topic}': {e}")
            raise

    async def subscribe(self, topic: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribe to a single topic and receive messages.

        Args:
            topic: Topic name to subscribe to

        Yields:
            Deserialized message dictionaries

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        pubsub = self.redis_client.pubsub()
        try:
            await pubsub.subscribe(topic)
            logger.info(f"Subscribed to topic: {topic}")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        yield data
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message from {topic}: {message['data']}")
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.close()
            logger.info(f"Unsubscribed from topic: {topic}")

    async def psubscribe(self, pattern: str) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Subscribe to topics matching a pattern and receive messages.

        Args:
            pattern: Pattern to match (e.g., "agent:*:updates")

        Yields:
            Tuples of (topic, message_dict)

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        pubsub = self.redis_client.pubsub()
        try:
            await pubsub.psubscribe(pattern)
            logger.info(f"Subscribed to pattern: {pattern}")

            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    try:
                        data = json.loads(message["data"])
                        yield (message["channel"], data)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to decode message from {message['channel']}: {message['data']}")
        finally:
            await pubsub.punsubscribe(pattern)
            await pubsub.close()
            logger.info(f"Unsubscribed from pattern: {pattern}")

    async def set_message_expiry(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        """
        Store a message with TTL (time-to-live).

        Args:
            key: Key to store message under
            value: Message dictionary
            ttl_seconds: Time-to-live in seconds (default: 1 hour)
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            message_json = json.dumps(value)
            await self.redis_client.setex(key, ttl_seconds, message_json)
            logger.debug(f"Stored message with TTL: {key} ({ttl_seconds}s)")
        except Exception as e:
            logger.error(f"Failed to store message: {e}")
            raise

    async def get_message(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored message.

        Args:
            key: Key to retrieve

        Returns:
            Message dictionary or None if not found
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve message: {e}")
            return None

    async def delete_message(self, key: str) -> bool:
        """
        Delete a stored message.

        Args:
            key: Key to delete

        Returns:
            True if deleted, False if not found
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            result = await self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            return False

    async def list_channels(self) -> List[str]:
        """
        List all active channels.

        Returns:
            List of channel names
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            channels_info = await self.redis_client.pubsub_channels()
            return list(channels_info) if channels_info else []
        except Exception as e:
            logger.error(f"Failed to list channels: {e}")
            return []

    async def get_channel_subscribers(self, channel: str) -> int:
        """
        Get number of subscribers to a channel.

        Args:
            channel: Channel name

        Returns:
            Number of subscribers
        """
        if not self.redis_client:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        try:
            result = await self.redis_client.pubsub_numsub(channel)
            return result.get(channel, 0) if result else 0
        except Exception as e:
            logger.error(f"Failed to get subscriber count: {e}")
            return 0


# ============================================================================
# Context Manager for Message Queue
# ============================================================================


class MessageQueueContext:
    """Context manager for message queue operations."""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.mq = MessageQueue(redis_url)

    async def __aenter__(self) -> MessageQueue:
        await self.mq.connect()
        return self.mq

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.mq.disconnect()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":

    async def example_publish_subscribe():
        """Example of publishing and subscribing to messages."""
        # Create message queue
        mq = MessageQueue("redis://localhost:6379")
        await mq.connect()

        try:
            # Example: Publish a message
            message = {
                "type": "task_assignment",
                "task_id": "123",
                "agent_id": "agent-001",
            }

            subscribers = await mq.publish("agent:tasks", message)
            print(f"Published message to {subscribers} subscribers")

            # Example: Subscribe to messages (in a separate task)
            async def subscriber():
                async for msg in mq.subscribe("agent:tasks"):
                    print(f"Received: {msg}")

            # Run subscriber in background
            # asyncio.create_task(subscriber())

        finally:
            await mq.disconnect()

    # To run: asyncio.run(example_publish_subscribe())
