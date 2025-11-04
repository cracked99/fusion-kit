"""
Channel management for inter-agent message routing.

Defines topic/channel naming conventions and subscription management.
"""

from enum import Enum
from typing import List, Optional
from uuid import UUID


class ChannelType(str, Enum):
    """Types of communication channels."""

    AGENT_TASKS = "agent:tasks"
    AGENT_STATUS = "agent:status"
    WORKFLOW_UPDATES = "workflow:updates"
    SYSTEM_EVENTS = "system:events"
    COLLABORATION = "collaboration:requests"
    RESULTS = "results:delivery"
    HEALTH_CHECKS = "health:checks"
    CUSTOM = "custom"


class ChannelManager:
    """
    Manages channel naming conventions and subscriptions.

    Provides consistent channel naming across the system.
    """

    # Channel naming patterns
    AGENT_TASKS_PATTERN = "agent:{agent_id}:tasks"
    AGENT_STATUS_PATTERN = "agent:{agent_id}:status"
    AGENT_HEARTBEAT_PATTERN = "agent:{agent_id}:heartbeat"
    WORKFLOW_PATTERN = "workflow:{workflow_id}:updates"
    PROJECT_PATTERN = "project:{project_id}:events"
    BROADCAST_PATTERN = "broadcast:*"
    SYSTEM_PATTERN = "system:*"

    @staticmethod
    def get_agent_task_channel(agent_id: UUID) -> str:
        """Get task assignment channel for an agent."""
        return f"agent:{agent_id}:tasks"

    @staticmethod
    def get_agent_status_channel(agent_id: UUID) -> str:
        """Get status update channel for an agent."""
        return f"agent:{agent_id}:status"

    @staticmethod
    def get_agent_heartbeat_channel(agent_id: UUID) -> str:
        """Get heartbeat channel for an agent."""
        return f"agent:{agent_id}:heartbeat"

    @staticmethod
    def get_workflow_channel(workflow_id: UUID) -> str:
        """Get update channel for a workflow."""
        return f"workflow:{workflow_id}:updates"

    @staticmethod
    def get_project_channel(project_id: UUID) -> str:
        """Get event channel for a project."""
        return f"project:{project_id}:events"

    @staticmethod
    def get_broadcast_channel() -> str:
        """Get broadcast channel for system-wide messages."""
        return "broadcast:system"

    @staticmethod
    def get_coordination_channel() -> str:
        """Get coordination channel for multi-agent coordination."""
        return "coordination:requests"

    @staticmethod
    def get_result_channel(task_id: UUID) -> str:
        """Get result delivery channel for a task."""
        return f"results:{task_id}"

    @staticmethod
    def get_agent_pattern(agent_id: UUID) -> str:
        """Get pattern to subscribe to all channels for an agent."""
        return f"agent:{agent_id}:*"

    @staticmethod
    def get_project_pattern(project_id: UUID) -> str:
        """Get pattern to subscribe to all project channels."""
        return f"project:{project_id}:*"

    @staticmethod
    def get_workflow_pattern(workflow_id: UUID) -> str:
        """Get pattern to subscribe to all workflow channels."""
        return f"workflow:{workflow_id}:*"


class ChannelSubscriptionManager:
    """Manages subscriptions for multiple channels."""

    def __init__(self):
        self.subscriptions: dict[str, List[str]] = {}

    def subscribe(self, subscriber_id: str, channel: str) -> None:
        """
        Add a subscription.

        Args:
            subscriber_id: ID of subscriber (agent, service, etc.)
            channel: Channel to subscribe to
        """
        if channel not in self.subscriptions:
            self.subscriptions[channel] = []
        if subscriber_id not in self.subscriptions[channel]:
            self.subscriptions[channel].append(subscriber_id)

    def unsubscribe(self, subscriber_id: str, channel: str) -> None:
        """
        Remove a subscription.

        Args:
            subscriber_id: ID of subscriber
            channel: Channel to unsubscribe from
        """
        if channel in self.subscriptions and subscriber_id in self.subscriptions[channel]:
            self.subscriptions[channel].remove(subscriber_id)
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]

    def get_subscribers(self, channel: str) -> List[str]:
        """
        Get all subscribers to a channel.

        Args:
            channel: Channel name

        Returns:
            List of subscriber IDs
        """
        return self.subscriptions.get(channel, [])

    def get_subscriptions(self, subscriber_id: str) -> List[str]:
        """
        Get all subscriptions for a subscriber.

        Args:
            subscriber_id: ID of subscriber

        Returns:
            List of subscribed channels
        """
        return [channel for channel, subscribers in self.subscriptions.items() if subscriber_id in subscribers]

    def is_subscribed(self, subscriber_id: str, channel: str) -> bool:
        """
        Check if subscriber is subscribed to channel.

        Args:
            subscriber_id: ID of subscriber
            channel: Channel name

        Returns:
            True if subscribed, False otherwise
        """
        return subscriber_id in self.subscriptions.get(channel, [])

    def clear_subscriber(self, subscriber_id: str) -> None:
        """
        Remove all subscriptions for a subscriber.

        Args:
            subscriber_id: ID of subscriber
        """
        channels_to_clean = []
        for channel, subscribers in self.subscriptions.items():
            if subscriber_id in subscribers:
                subscribers.remove(subscriber_id)
                if not subscribers:
                    channels_to_clean.append(channel)

        for channel in channels_to_clean:
            del self.subscriptions[channel]


# ============================================================================
# Topic Routing
# ============================================================================


class TopicRouter:
    """Routes messages to appropriate topics based on content type."""

    @staticmethod
    def route_task_assignment(agent_id: UUID, task_id: UUID) -> str:
        """Get topic for task assignment."""
        return ChannelManager.get_agent_task_channel(agent_id)

    @staticmethod
    def route_status_update(agent_id: UUID) -> str:
        """Get topic for status updates."""
        return ChannelManager.get_agent_status_channel(agent_id)

    @staticmethod
    def route_workflow_update(workflow_id: UUID) -> str:
        """Get topic for workflow updates."""
        return ChannelManager.get_workflow_channel(workflow_id)

    @staticmethod
    def route_result_delivery(task_id: UUID) -> str:
        """Get topic for result delivery."""
        return ChannelManager.get_result_channel(task_id)

    @staticmethod
    def route_coordination_request(project_id: UUID) -> str:
        """Get topic for coordination requests."""
        return ChannelManager.get_project_channel(project_id)

    @staticmethod
    def route_system_event() -> str:
        """Get topic for system events."""
        return ChannelManager.get_broadcast_channel()


if __name__ == "__main__":
    from uuid import uuid4

    # Example usage
    agent_id = uuid4()
    workflow_id = uuid4()

    print(f"Agent task channel: {ChannelManager.get_agent_task_channel(agent_id)}")
    print(f"Workflow channel: {ChannelManager.get_workflow_channel(workflow_id)}")
    print(f"Agent pattern: {ChannelManager.get_agent_pattern(agent_id)}")

    # Test subscription manager
    mgr = ChannelSubscriptionManager()
    mgr.subscribe("agent-001", "agent:tasks")
    mgr.subscribe("agent-002", "agent:tasks")
    print(f"Subscribers to agent:tasks: {mgr.get_subscribers('agent:tasks')}")
