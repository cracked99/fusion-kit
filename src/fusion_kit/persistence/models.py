"""
SQLAlchemy models for multi-agent orchestration framework.

Defines 10 core entities:
1. Agent - AI agent instances with lifecycle
2. Task - Units of work assigned to agents
3. Workspace - Isolated working directories
4. Workflow - Multi-agent coordinated processes
5. Event - System occurrences
6. Message - Inter-agent communication
7. Capability - Skills/specializations
8. Project - Development projects
9. ResourceMetrics - Time-series resource usage
10. ProviderConfig - LLM provider settings
"""

from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UUID as SQLUuid,
    UniqueConstraint,
    Index,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# ============================================================================
# Enums
# ============================================================================


class AgentState(str, Enum):
    """Agent lifecycle states."""

    SPAWNING = "spawning"
    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"


class TaskState(str, Enum):
    """Task execution states."""

    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowState(str, Enum):
    """Workflow execution states."""

    DRAFT = "draft"
    VALIDATING = "validating"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventSeverity(str, Enum):
    """Event severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DeliveryStatus(str, Enum):
    """Message delivery states."""

    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"


# ============================================================================
# 1. Agent
# ============================================================================


class Agent(Base):
    """
    Represents an AI agent instance with lifecycle, capabilities, and provider configuration.
    """

    __tablename__ = "agents"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)

    # State & Lifecycle
    state = Column(
        SQLEnum("spawning", "idle", "working", "paused", "error", "terminated", name="agent_state"),
        nullable=False,
        default="spawning",
    )
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_heartbeat = Column(DateTime, nullable=True)

    # Configuration
    workspace_path = Column(String(512), nullable=False, unique=True)
    provider_id = Column(SQLUuid(as_uuid=True), ForeignKey("provider_configs.id"), nullable=False)
    model_name = Column(String(128), nullable=False)

    # Capabilities & Metadata
    capabilities = Column(JSON, nullable=False, default=list)
    metadata = Column(JSON, nullable=False, default=dict)
    message_subscriptions = Column(JSON, nullable=False, default=list)

    # Relationships
    project_id = Column(SQLUuid(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="agents")
    provider_config = relationship("ProviderConfig")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("Event", foreign_keys="Event.source_agent_id", back_populates="source_agent")
    metrics = relationship("ResourceMetrics", back_populates="agent", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_agent_state", "state"),
        Index("idx_agent_project", "project_id"),
        Index("idx_agent_updated", "updated_at"),
    )


# ============================================================================
# 2. Task
# ============================================================================


class Task(Base):
    """Unit of work assigned to an agent with priority, dependencies, and execution state."""

    __tablename__ = "tasks"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)

    # Assignment & Priority
    agent_id = Column(SQLUuid(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    priority = Column(Integer, nullable=False, default=0)
    required_capabilities = Column(JSON, nullable=False, default=list)

    # State & Timing
    state = Column(
        SQLEnum("queued", "assigned", "running", "completed", "failed", "cancelled", name="task_state"),
        nullable=False,
        default="queued",
    )
    queued_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Dependencies
    dependencies = Column(JSON, nullable=False, default=list)

    # Input/Output
    input_artifacts = Column(JSON, nullable=False, default=dict)
    output_artifacts = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Communication
    communication_channels = Column(JSON, nullable=False, default=list)

    # Relationships
    workflow_id = Column(SQLUuid(as_uuid=True), ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("Workflow", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")

    __table_args__ = (
        Index("idx_task_state", "state"),
        Index("idx_task_agent", "agent_id"),
        Index("idx_task_workflow", "workflow_id"),
        Index("idx_task_priority", "priority", "queued_at"),
    )


# ============================================================================
# 3. Workspace
# ============================================================================


class Workspace(Base):
    """Isolated working directory for an agent with initialization state and file management."""

    __tablename__ = "workspaces"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(SQLUuid(as_uuid=True), ForeignKey("agents.id"), nullable=False, unique=True)

    # Paths
    root_path = Column(String(512), nullable=False, unique=True)
    projects_path = Column(String(512), nullable=False)
    logs_path = Column(String(512), nullable=False)

    # Initialization State
    initialized = Column(Boolean, nullable=False, default=False)
    initialization_error = Column(Text, nullable=True)

    # Configuration
    agent_config = Column(JSON, nullable=False, default=dict)
    environment_variables = Column(JSON, nullable=False, default=dict)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    size_bytes = Column(BigInteger, nullable=True)
    file_count = Column(Integer, nullable=True)

    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])

    __table_args__ = (
        Index("idx_workspace_agent", "agent_id"),
        Index("idx_workspace_initialized", "initialized"),
    )


# ============================================================================
# 4. Workflow
# ============================================================================


class Workflow(Base):
    """Multi-agent coordinated process with task dependencies (DAG) and execution state."""

    __tablename__ = "workflows"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Definition
    dag_definition = Column(JSON, nullable=False)
    execution_parameters = Column(JSON, nullable=False, default=dict)

    # State
    state = Column(
        SQLEnum("draft", "validating", "ready", "running", "completed", "failed", "cancelled", name="workflow_state"),
        nullable=False,
        default="draft",
    )

    # Timing
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Message Flow
    message_flow_definitions = Column(JSON, nullable=False, default=dict)

    # Relationships
    project_id = Column(SQLUuid(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow", cascade="all, delete-orphan")
    version = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        Index("idx_workflow_state", "state"),
        Index("idx_workflow_project", "project_id"),
        Index("idx_workflow_created", "created_at"),
    )


# ============================================================================
# 5. Event
# ============================================================================


class Event(Base):
    """System occurrence with timestamp, source, severity for monitoring and debugging."""

    __tablename__ = "events"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Classification
    event_type = Column(String(128), nullable=False, index=True)
    severity = Column(
        SQLEnum("debug", "info", "warning", "error", "critical", name="event_severity"),
        nullable=False,
        default="info",
    )

    # Source
    source_agent_id = Column(SQLUuid(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    source_component = Column(String(128), nullable=True)

    # Data
    data = Column(JSON, nullable=False, default=dict)
    message = Column(Text, nullable=True)

    # Message Queue Info
    message_queue_topic = Column(String(255), nullable=True)

    # Relationships
    source_agent = relationship("Agent", foreign_keys=[source_agent_id], back_populates="events")

    __table_args__ = (
        Index("idx_event_timestamp", "timestamp"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_agent", "source_agent_id"),
        Index("idx_event_severity", "severity"),
        Index("idx_event_composite", "event_type", "timestamp"),
    )


# ============================================================================
# 6. Message
# ============================================================================


class Message(Base):
    """Inter-agent communication unit with routing, payload, and delivery tracking."""

    __tablename__ = "messages"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Routing
    sender_agent_id = Column(SQLUuid(as_uuid=True), ForeignKey("agents.id"), nullable=False)
    recipient_agent_ids = Column(JSON, nullable=True)
    topic = Column(String(255), nullable=False, index=True)

    # Content
    payload = Column(JSON, nullable=False)
    message_type = Column(String(128), nullable=False)

    # Delivery
    delivery_status = Column(
        SQLEnum("pending", "delivered", "failed", "expired", name="delivery_status"),
        nullable=False,
        default="pending",
    )
    delivered_at = Column(DateTime, nullable=True)
    expiry_at = Column(DateTime, nullable=True)

    # Relationships
    sender = relationship("Agent", foreign_keys=[sender_agent_id])

    __table_args__ = (
        Index("idx_message_timestamp", "timestamp"),
        Index("idx_message_sender", "sender_agent_id"),
        Index("idx_message_topic", "topic"),
        Index("idx_message_status", "delivery_status"),
    )


# ============================================================================
# 7. Capability
# ============================================================================


class Capability(Base):
    """Skill or specialization that can be possessed by agents and required by tasks."""

    __tablename__ = "capabilities"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False, unique=True, index=True)

    # Description
    description = Column(Text, nullable=True)
    category = Column(String(64), nullable=True)

    # Metadata
    metadata = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


# ============================================================================
# 8. Project
# ============================================================================


class Project(Base):
    """Development project containing agents, tasks, workflows, and configuration."""

    __tablename__ = "projects"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    # Configuration
    message_queue_config = Column(JSON, nullable=False, default=dict)
    default_provider_id = Column(SQLUuid(as_uuid=True), ForeignKey("provider_configs.id"), nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON, nullable=False, default=dict)

    # Relationships
    agents = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="project", cascade="all, delete-orphan")
    default_provider = relationship("ProviderConfig", foreign_keys=[default_provider_id])

    __table_args__ = (Index("idx_project_name", "name"), Index("idx_project_updated", "updated_at"))


# ============================================================================
# 9. ResourceMetrics
# ============================================================================


class ResourceMetrics(Base):
    """Time-series resource consumption data per agent."""

    __tablename__ = "resource_metrics"

    # Identity & Timing
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    agent_id = Column(SQLUuid(as_uuid=True), ForeignKey("agents.id"), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Resource Usage
    cpu_percent = Column(Float, nullable=True)
    memory_mb = Column(Float, nullable=True)
    disk_io_read_mb = Column(Float, nullable=True)
    disk_io_write_mb = Column(Float, nullable=True)

    # API Usage (per provider)
    api_calls_count = Column(Integer, nullable=False, default=0)
    api_provider = Column(String(128), nullable=True)
    api_tokens_used = Column(Integer, nullable=True)
    api_cost_usd = Column(Float, nullable=True)

    # Relationships
    agent = relationship("Agent", back_populates="metrics")

    __table_args__ = (Index("idx_metrics_agent_time", "agent_id", "timestamp"), Index("idx_metrics_timestamp", "timestamp"))


# ============================================================================
# 10. ProviderConfig
# ============================================================================


class ProviderConfig(Base):
    """LLM provider settings with credentials, endpoints, rate limits."""

    __tablename__ = "provider_configs"

    # Identity
    id = Column(SQLUuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(128), nullable=False, unique=True, index=True)

    # Connection
    api_endpoint = Column(String(512), nullable=False)
    auth_type = Column(String(64), nullable=False)
    credentials = Column(JSON, nullable=False)

    # Capabilities
    model_catalog = Column(JSON, nullable=False, default=list)
    rate_limits = Column(JSON, nullable=False, default=dict)

    # Extensibility
    provider_type = Column(String(128), nullable=False)
    custom_adapter_class = Column(String(255), nullable=True)

    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    enabled = Column(Boolean, nullable=False, default=True)
    metadata = Column(JSON, nullable=False, default=dict)

    __table_args__ = (Index("idx_provider_name", "name"), Index("idx_provider_enabled", "enabled"))
