# Data Model: Multi-Agent Orchestration Framework

**Date**: 2025-11-04  
**Purpose**: Entity definitions and relationships for persistence layer

## Overview

This document defines the data models for all entities in the multi-agent framework, including SQLAlchemy ORM mappings, relationships, and database schema.

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Project    │──────<│    Agent     │──────<│   Workspace  │
└──────────────┘       └──────────────┘       └──────────────┘
       │                      │                       
       │                      │                       
       ▼                      ▼                       
┌──────────────┐       ┌──────────────┐              
│   Workflow   │──────<│     Task     │              
└──────────────┘       └──────────────┘              
       │                      │                       
       │                      └────────┐              
       ▼                               ▼              
┌──────────────┐              ┌──────────────┐       
│    Event     │◀─────────────│   Message    │       
└──────────────┘              └──────────────┘       
                                                      
┌──────────────┐       ┌──────────────┐              
│  Capability  │       │ProviderConfig│              
└──────────────┘       └──────────────┘              
        △                      △                      
        │                      │                      
        └──────────────────────┘                      
               (many-to-many)                         

┌──────────────┐
│ResourceMetric│
└──────────────┘
        │
        ▼
  (time-series)
```

## 1. Agent

**Description**: Represents an AI agent instance with lifecycle, capabilities, and provider configuration.

**Attributes**:
```python
class Agent(Base):
    __tablename__ = "agents"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False)
    
    # State & Lifecycle
    state: AgentState = Column(
        Enum('spawning', 'idle', 'working', 'paused', 'error', 'terminated', name='agent_state'),
        nullable=False,
        default='spawning'
    )
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_heartbeat: datetime = Column(DateTime, nullable=True)
    
    # Configuration
    workspace_path: str = Column(String(512), nullable=False, unique=True)
    provider_id: UUID = Column(UUID(as_uuid=True), ForeignKey('provider_configs.id'), nullable=False)
    model_name: str = Column(String(128), nullable=False)  # e.g., "claude-3-opus", "gpt-4"
    
    # Capabilities & Metadata
    capabilities: List[str] = Column(JSON, nullable=False, default=list)  # ["planning", "coding", "review"]
    metadata: dict = Column(JSON, nullable=False, default=dict)  # Extensible metadata
    message_subscriptions: List[str] = Column(JSON, nullable=False, default=list)  # Redis topics subscribed to
    
    # Relationships
    project_id: UUID = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="agents")
    provider_config = relationship("ProviderConfig")
    tasks = relationship("Task", back_populates="agent", cascade="all, delete-orphan")
    events = relationship("Event", foreign_keys="Event.source_agent_id", back_populates="source_agent")
    metrics = relationship("ResourceMetrics", back_populates="agent", cascade="all, delete-orphan")
```

**Indexes**:
```sql
CREATE INDEX idx_agent_state ON agents(state);
CREATE INDEX idx_agent_project ON agents(project_id);
CREATE INDEX idx_agent_updated ON agents(updated_at DESC);
```

**Lifecycle States**:
- `spawning`: Being created, workspace initialization in progress
- `idle`: Ready to accept tasks
- `working`: Currently executing task
- `paused`: Suspended, state preserved
- `error`: Encountered unrecoverable error
- `terminated`: Shut down, resources released

---

## 2. Task

**Description**: Unit of work assigned to an agent with priority, dependencies, and execution state.

**Attributes**:
```python
class Task(Base):
    __tablename__ = "tasks"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=False)
    
    # Assignment & Priority
    agent_id: UUID = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=True)  # NULL = unassigned
    priority: int = Column(Integer, nullable=False, default=0)  # Higher = more important
    required_capabilities: List[str] = Column(JSON, nullable=False, default=list)
    
    # State & Timing
    state: TaskState = Column(
        Enum('queued', 'assigned', 'running', 'completed', 'failed', 'cancelled', name='task_state'),
        nullable=False,
        default='queued'
    )
    queued_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: datetime = Column(DateTime, nullable=True)
    completed_at: datetime = Column(DateTime, nullable=True)
    
    # Dependencies
    dependencies: List[UUID] = Column(JSON, nullable=False, default=list)  # List of task IDs
    
    # Input/Output
    input_artifacts: dict = Column(JSON, nullable=False, default=dict)  # Files, parameters, context
    output_artifacts: dict = Column(JSON, nullable=True)  # Results, generated files
    error_message: str = Column(Text, nullable=True)
    
    # Communication
    communication_channels: List[str] = Column(JSON, nullable=False, default=list)  # Redis topics for this task
    
    # Relationships
    workflow_id: UUID = Column(UUID(as_uuid=True), ForeignKey('workflows.id'), nullable=True)  # NULL = standalone task
    workflow = relationship("Workflow", back_populates="tasks")
    agent = relationship("Agent", back_populates="tasks")
```

**Indexes**:
```sql
CREATE INDEX idx_task_state ON tasks(state);
CREATE INDEX idx_task_agent ON tasks(agent_id);
CREATE INDEX idx_task_workflow ON tasks(workflow_id);
CREATE INDEX idx_task_priority ON tasks(priority DESC, queued_at ASC);
```

**Task States**:
- `queued`: Waiting for assignment
- `assigned`: Assigned to agent, not started
- `running`: Agent executing
- `completed`: Successfully finished
- `failed`: Error occurred
- `cancelled`: Explicitly cancelled

---

## 3. Workspace

**Description**: Isolated working directory for an agent with initialization state and file management.

**Attributes**:
```python
class Workspace(Base):
    __tablename__ = "workspaces"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: UUID = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False, unique=True)
    
    # Paths
    root_path: str = Column(String(512), nullable=False, unique=True)
    projects_path: str = Column(String(512), nullable=False)
    logs_path: str = Column(String(512), nullable=False)
    
    # Initialization State
    initialized: bool = Column(Boolean, nullable=False, default=False)
    initialization_error: str = Column(Text, nullable=True)
    
    # Configuration
    agent_config: dict = Column(JSON, nullable=False, default=dict)  # Agent-specific settings
    environment_variables: dict = Column(JSON, nullable=False, default=dict)  # Isolated env vars
    
    # Metadata
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    size_bytes: int = Column(BigInteger, nullable=True)  # Disk usage (updated periodically)
    file_count: int = Column(Integer, nullable=True)
    
    # Relationships
    agent = relationship("Agent", foreign_keys=[agent_id])
```

**Indexes**:
```sql
CREATE INDEX idx_workspace_agent ON workspaces(agent_id);
CREATE INDEX idx_workspace_initialized ON workspaces(initialized);
```

---

## 4. Workflow

**Description**: Multi-agent coordinated process with task dependencies (DAG) and execution state.

**Attributes**:
```python
class Workflow(Base):
    __tablename__ = "workflows"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    
    # Definition
    dag_definition: dict = Column(JSON, nullable=False)  # {"nodes": [...], "edges": [...]}
    execution_parameters: dict = Column(JSON, nullable=False, default=dict)
    
    # State
    state: WorkflowState = Column(
        Enum('draft', 'validating', 'ready', 'running', 'completed', 'failed', 'cancelled', name='workflow_state'),
        nullable=False,
        default='draft'
    )
    
    # Timing
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at: datetime = Column(DateTime, nullable=True)
    completed_at: datetime = Column(DateTime, nullable=True)
    
    # Message Flow
    message_flow_definitions: dict = Column(JSON, nullable=False, default=dict)  # Inter-agent communication routes
    
    # Relationships
    project_id: UUID = Column(UUID(as_uuid=True), ForeignKey('projects.id'), nullable=False)
    project = relationship("Project", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow", cascade="all, delete-orphan")
    version: int = Column(Integer, nullable=False, default=1)  # For workflow versioning
```

**Indexes**:
```sql
CREATE INDEX idx_workflow_state ON workflows(state);
CREATE INDEX idx_workflow_project ON workflows(project_id);
CREATE INDEX idx_workflow_created ON workflows(created_at DESC);
```

**Workflow States**:
- `draft`: Being designed
- `validating`: Checking for cycles, invalid dependencies
- `ready`: Validated, can be started
- `running`: Tasks executing
- `completed`: All tasks finished
- `failed`: One or more tasks failed
- `cancelled`: Explicitly stopped

---

## 5. Event

**Description**: System occurrence with timestamp, source, severity for monitoring and debugging.

**Attributes**:
```python
class Event(Base):
    __tablename__ = "events"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Classification
    event_type: str = Column(String(128), nullable=False, index=True)  # "agent.spawned", "task.completed", etc.
    severity: EventSeverity = Column(
        Enum('debug', 'info', 'warning', 'error', 'critical', name='event_severity'),
        nullable=False,
        default='info'
    )
    
    # Source
    source_agent_id: UUID = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=True)  # NULL = system event
    source_component: str = Column(String(128), nullable=True)  # e.g., "delegation_daemon", "message_queue"
    
    # Data
    data: dict = Column(JSON, nullable=False, default=dict)  # Event-specific payload
    message: str = Column(Text, nullable=True)  # Human-readable description
    
    # Message Queue Info
    message_queue_topic: str = Column(String(255), nullable=True)  # Redis topic this event published to
    
    # Relationships
    source_agent = relationship("Agent", foreign_keys=[source_agent_id], back_populates="events")
```

**Indexes**:
```sql
CREATE INDEX idx_event_timestamp ON events(timestamp DESC);
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_event_agent ON events(source_agent_id);
CREATE INDEX idx_event_severity ON events(severity);
CREATE INDEX idx_event_composite ON events(event_type, timestamp DESC);  # Common query pattern
```

**Event Types** (examples):
- `agent.spawned`, `agent.paused`, `agent.resumed`, `agent.terminated`
- `task.queued`, `task.assigned`, `task.started`, `task.completed`, `task.failed`
- `workflow.started`, `workflow.completed`, `workflow.failed`
- `message.sent`, `message.delivered`, `message.failed`
- `system.started`, `system.shutdown`, `system.error`

---

## 6. Message

**Description**: Inter-agent communication unit with routing, payload, and delivery tracking.

**Attributes**:
```python
class Message(Base):
    __tablename__ = "messages"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Routing
    sender_agent_id: UUID = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False)
    recipient_agent_ids: List[UUID] = Column(JSON, nullable=True)  # NULL = broadcast
    topic: str = Column(String(255), nullable=False, index=True)  # Redis topic
    
    # Content
    payload: dict = Column(JSON, nullable=False)  # Actual message data
    message_type: str = Column(String(128), nullable=False)  # "task_assignment", "status_update", "collaboration_request"
    
    # Delivery
    delivery_status: DeliveryStatus = Column(
        Enum('pending', 'delivered', 'failed', 'expired', name='delivery_status'),
        nullable=False,
        default='pending'
    )
    delivered_at: datetime = Column(DateTime, nullable=True)
    expiry_at: datetime = Column(DateTime, nullable=True)  # TTL for messages
    
    # Relationships
    sender = relationship("Agent", foreign_keys=[sender_agent_id])
```

**Indexes**:
```sql
CREATE INDEX idx_message_timestamp ON messages(timestamp DESC);
CREATE INDEX idx_message_sender ON messages(sender_agent_id);
CREATE INDEX idx_message_topic ON messages(topic);
CREATE INDEX idx_message_status ON messages(delivery_status);
```

---

## 7. Capability

**Description**: Skill or specialization that can be possessed by agents and required by tasks.

**Attributes**:
```python
class Capability(Base):
    __tablename__ = "capabilities"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(128), nullable=False, unique=True, index=True)  # "python_development", "code_review"
    
    # Description
    description: str = Column(Text, nullable=True)
    category: str = Column(String(64), nullable=True)  # "development", "testing", "documentation"
    
    # Metadata
    metadata: dict = Column(JSON, nullable=False, default=dict)  # Additional attributes
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
```

**Note**: Agent capabilities stored as JSON list in `agents.capabilities` for simplicity. This table provides capability registry for validation and discovery.

---

## 8. Project

**Description**: Development project containing agents, tasks, workflows, and configuration.

**Attributes**:
```python
class Project(Base):
    __tablename__ = "projects"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(255), nullable=False, unique=True, index=True)
    description: str = Column(Text, nullable=True)
    
    # Configuration
    message_queue_config: dict = Column(JSON, nullable=False, default=dict)  # Redis connection, topics
    default_provider_id: UUID = Column(UUID(as_uuid=True), ForeignKey('provider_configs.id'), nullable=True)
    
    # Metadata
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata: dict = Column(JSON, nullable=False, default=dict)
    
    # Relationships
    agents = relationship("Agent", back_populates="project", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="project", cascade="all, delete-orphan")
    default_provider = relationship("ProviderConfig", foreign_keys=[default_provider_id])
```

**Indexes**:
```sql
CREATE INDEX idx_project_name ON projects(name);
CREATE INDEX idx_project_updated ON projects(updated_at DESC);
```

---

## 9. ResourceMetrics

**Description**: Time-series resource consumption data per agent.

**Attributes**:
```python
class ResourceMetrics(Base):
    __tablename__ = "resource_metrics"
    
    # Identity & Timing
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: UUID = Column(UUID(as_uuid=True), ForeignKey('agents.id'), nullable=False, index=True)
    timestamp: datetime = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Resource Usage
    cpu_percent: float = Column(Float, nullable=True)  # 0-100
    memory_mb: float = Column(Float, nullable=True)
    disk_io_read_mb: float = Column(Float, nullable=True)
    disk_io_write_mb: float = Column(Float, nullable=True)
    
    # API Usage (per provider)
    api_calls_count: int = Column(Integer, nullable=False, default=0)
    api_provider: str = Column(String(128), nullable=True)
    api_tokens_used: int = Column(Integer, nullable=True)
    api_cost_usd: float = Column(Float, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="metrics")
```

**Indexes**:
```sql
CREATE INDEX idx_metrics_agent_time ON resource_metrics(agent_id, timestamp DESC);
CREATE INDEX idx_metrics_timestamp ON resource_metrics(timestamp DESC);
```

**Collection Strategy**: Metrics collected every 30 seconds, retained for 30 days (configurable).

---

## 10. ProviderConfig

**Description**: LLM provider settings with credentials, endpoints, rate limits.

**Attributes**:
```python
class ProviderConfig(Base):
    __tablename__ = "provider_configs"
    
    # Identity
    id: UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: str = Column(String(128), nullable=False, unique=True, index=True)  # "openrouter", "anthropic", "openai"
    
    # Connection
    api_endpoint: str = Column(String(512), nullable=False)
    auth_type: str = Column(String(64), nullable=False)  # "bearer_token", "api_key", "oauth"
    credentials: dict = Column(JSON, nullable=False)  # Encrypted: {"api_key": "sk-..."} - use encryption at rest
    
    # Capabilities
    model_catalog: List[str] = Column(JSON, nullable=False, default=list)  # Available models
    rate_limits: dict = Column(JSON, nullable=False, default=dict)  # {"requests_per_minute": 60, "tokens_per_minute": 10000}
    
    # Extensibility
    provider_type: str = Column(String(128), nullable=False)  # "openrouter", "custom"
    custom_adapter_class: str = Column(String(255), nullable=True)  # Python class path for custom providers
    
    # Metadata
    created_at: datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    enabled: bool = Column(Boolean, nullable=False, default=True)
    metadata: dict = Column(JSON, nullable=False, default=dict)
```

**Indexes**:
```sql
CREATE INDEX idx_provider_name ON provider_configs(name);
CREATE INDEX idx_provider_enabled ON provider_configs(enabled);
```

**Security Note**: `credentials` field should use SQLAlchemy encrypted type (e.g., `sqlalchemy_utils.EncryptedType`) in production.

---

## Relationships Summary

```
Project (1) ←→ (N) Agent
Project (1) ←→ (N) Workflow
Project (N) ←→ (1) ProviderConfig [default_provider]

Agent (1) ←→ (1) Workspace
Agent (1) ←→ (N) Task
Agent (1) ←→ (N) Event
Agent (1) ←→ (N) ResourceMetrics
Agent (1) ←→ (N) Message [as sender]
Agent (N) ←→ (1) ProviderConfig

Workflow (1) ←→ (N) Task

Task (N) ←→ (1) Agent [nullable, unassigned allowed]
Task (N) ←→ (1) Workflow [nullable, standalone tasks allowed]

Message (N) ←→ (1) Agent [sender]

Event (N) ←→ (1) Agent [source, nullable for system events]
```

---

## Database Initialization

```python
# Base class for all models
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

# Engine setup
DATABASE_URL = "sqlite+aiosqlite:///./fusion_kit.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

---

## Schema Migrations

Use Alembic for schema versioning:

```bash
# Initialize Alembic
alembic init alembic

# Generate migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

---

## Data Validation

All models use Pydantic schemas for API validation:

```python
# Example Pydantic schema for Agent
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class AgentState(str, Enum):
    SPAWNING = "spawning"
    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    ERROR = "error"
    TERMINATED = "terminated"

class AgentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    capabilities: List[str] = Field(default_factory=list)
    provider_id: UUID
    model_name: str
    project_id: UUID

class AgentResponse(BaseModel):
    id: UUID
    name: str
    state: AgentState
    capabilities: List[str]
    workspace_path: str
    created_at: datetime
    
    class Config:
        from_attributes = True  # Enable ORM mode
```
