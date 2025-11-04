"""
WebSocket connection management for real-time updates.

Handles client connections and broadcasts real-time events.
"""

import json
import logging
from typing import List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates.

    Allows broadcasting of events to all connected clients.
    """

    def __init__(self):
        """Initialize connection manager."""
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Send a message to all connected clients.

        Args:
            message: Dictionary message to broadcast
        """
        disconnected = []

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error sending to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    async def broadcast_event(self, event_type: str, data: dict):
        """
        Broadcast a typed event to all clients.

        Args:
            event_type: Type of event (e.g., 'agent_status', 'task_update')
            data: Event data
        """
        message = {
            "type": event_type,
            "data": data,
        }
        await self.broadcast(message)

    async def send_to_client(self, websocket: WebSocket, message: dict):
        """
        Send a message to a specific client.

        Args:
            websocket: Target WebSocket connection
            message: Message to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Error sending to specific client: {e}")
            await self.disconnect(websocket)

    def get_active_connections_count(self) -> int:
        """
        Get number of active connections.

        Returns:
            Number of active WebSocket connections
        """
        return len(self.active_connections)


# ============================================================================
# Event Broadcasting Helpers
# ============================================================================


async def broadcast_agent_status(manager: ConnectionManager, agent_id: str, state: str, metadata: dict = None):
    """
    Broadcast an agent status update.

    Args:
        manager: ConnectionManager instance
        agent_id: ID of the agent
        state: New state of the agent
        metadata: Optional additional metadata
    """
    event_data = {
        "agent_id": agent_id,
        "state": state,
        "timestamp": str(__import__("datetime").datetime.utcnow()),
    }
    if metadata:
        event_data.update(metadata)

    await manager.broadcast_event("agent_status", event_data)


async def broadcast_task_update(manager: ConnectionManager, task_id: str, state: str, progress: int = None):
    """
    Broadcast a task update.

    Args:
        manager: ConnectionManager instance
        task_id: ID of the task
        state: New state of the task
        progress: Optional progress percentage (0-100)
    """
    event_data = {
        "task_id": task_id,
        "state": state,
        "timestamp": str(__import__("datetime").datetime.utcnow()),
    }
    if progress is not None:
        event_data["progress"] = progress

    await manager.broadcast_event("task_update", event_data)


async def broadcast_event_occurred(manager: ConnectionManager, event_type: str, severity: str, message: str):
    """
    Broadcast a system event.

    Args:
        manager: ConnectionManager instance
        event_type: Type of event
        severity: Severity level (debug, info, warning, error, critical)
        message: Event message
    """
    event_data = {
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "timestamp": str(__import__("datetime").datetime.utcnow()),
    }
    await manager.broadcast_event("system_event", event_data)
