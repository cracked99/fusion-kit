"""
Pydantic models for inter-agent message communication.

Defines message types, schemas, and serialization for agent-to-agent communication.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of inter-agent messages."""

    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    COLLABORATION_REQUEST = "collaboration_request"
    HEARTBEAT = "heartbeat"
    ERROR_REPORT = "error_report"
    RESULT_DELIVERY = "result_delivery"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    WORKFLOW_DIRECTIVE = "workflow_directive"
    CUSTOM = "custom"


class DeliveryStatus(str, Enum):
    """Message delivery states."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


# ============================================================================
# Message Schemas
# ============================================================================


class MessagePayload(BaseModel):
    """
    Base message payload.

    All inter-agent messages contain this structure.
    """

    message_type: MessageType
    content: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = Field(default=None, description="ID for correlating request/response pairs")

    class Config:
        use_enum_values = True


class Message(BaseModel):
    """
    Complete message structure for storage and transmission.

    Includes routing information, payload, and delivery tracking.
    """

    id: UUID
    timestamp: datetime
    sender_agent_id: UUID
    recipient_agent_ids: Optional[List[UUID]] = Field(
        default=None, description="None means broadcast to all subscribed agents"
    )
    topic: str = Field(..., description="Redis pub/sub topic")
    payload: MessagePayload
    message_type: str
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    delivered_at: Optional[datetime] = None
    expiry_at: Optional[datetime] = None

    class Config:
        use_enum_values = True


class TaskAssignmentMessage(BaseModel):
    """Message for assigning a task to an agent."""

    task_id: UUID
    task_name: str
    description: str
    required_capabilities: List[str] = Field(default_factory=list)
    input_artifacts: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 0
    dependencies: List[UUID] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class StatusUpdateMessage(BaseModel):
    """Message for updating agent or task status."""

    source_id: UUID
    source_type: str = Field(..., description="'agent' or 'task'")
    current_state: str
    previous_state: Optional[str] = None
    progress_percent: Optional[int] = None
    details: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class CollaborationRequestMessage(BaseModel):
    """Message requesting collaboration from another agent."""

    requesting_agent_id: UUID
    capability_needed: str
    context: Dict[str, Any] = Field(default_factory=dict)
    required_by: Optional[datetime] = None
    reward_or_incentive: Optional[str] = None

    class Config:
        use_enum_values = True


class HeartbeatMessage(BaseModel):
    """Agent heartbeat message for liveness detection."""

    agent_id: UUID
    agent_state: str
    active_tasks_count: int = 0
    memory_mb: Optional[float] = None
    cpu_percent: Optional[float] = None

    class Config:
        use_enum_values = True


class ErrorReportMessage(BaseModel):
    """Message reporting an error."""

    source_id: UUID
    error_type: str
    error_message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    severity: str = Field(default="error", description="debug, info, warning, error, critical")

    class Config:
        use_enum_values = True


class ResultDeliveryMessage(BaseModel):
    """Message delivering task results."""

    task_id: UUID
    status: str = Field(..., description="'completed' or 'failed'")
    output_artifacts: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_seconds: Optional[float] = None

    class Config:
        use_enum_values = True


class CapabilityQueryMessage(BaseModel):
    """Message querying available capabilities."""

    query_type: str = Field(..., description="'search', 'all', or specific capability name")
    filters: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        use_enum_values = True


class CapabilityResponseMessage(BaseModel):
    """Message responding with capability information."""

    capabilities: List[str]
    agent_id: UUID
    query_correlation_id: Optional[str] = None

    class Config:
        use_enum_values = True


# ============================================================================
# Message Factory
# ============================================================================


def create_message(
    message_type: MessageType,
    sender_agent_id: UUID,
    content: Dict[str, Any],
    topic: str,
    recipient_agent_ids: Optional[List[UUID]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> MessagePayload:
    """
    Factory function to create message payloads.

    Args:
        message_type: Type of message
        sender_agent_id: ID of sending agent
        content: Message content (specific to message type)
        topic: Redis topic for publishing
        recipient_agent_ids: Target agents (None = broadcast)
        metadata: Optional metadata

    Returns:
        MessagePayload ready for serialization
    """
    return MessagePayload(
        message_type=message_type,
        content={
            "sender_agent_id": str(sender_agent_id),
            "recipients": [str(id) for id in (recipient_agent_ids or [])],
            **content,
        },
        metadata=metadata or {},
    )
