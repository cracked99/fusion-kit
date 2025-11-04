"""
Pydantic schemas for FastAPI endpoints.

Defines request/response models for all API endpoints.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ============================================================================
# Health & Status
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Response from health check endpoint."""

    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"
    database: str = "connected"
    redis: str = "connected"


# ============================================================================
# Agent Schemas
# ============================================================================


class AgentCreate(BaseModel):
    """Request to create an agent."""

    name: str = Field(..., min_length=1, max_length=255)
    capabilities: List[str] = Field(default_factory=list)
    provider_id: UUID
    model_name: str
    project_id: UUID
    workspace_path: Optional[str] = None


class AgentUpdate(BaseModel):
    """Request to update an agent."""

    name: Optional[str] = None
    state: Optional[str] = None
    capabilities: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentResponse(BaseModel):
    """Response with agent details."""

    id: UUID
    name: str
    state: str
    capabilities: List[str]
    workspace_path: str
    created_at: datetime
    updated_at: datetime
    model_name: str

    class Config:
        from_attributes = True


# ============================================================================
# Task Schemas
# ============================================================================


class TaskCreate(BaseModel):
    """Request to create a task."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str
    agent_id: Optional[UUID] = None
    priority: int = Field(default=0, ge=0)
    required_capabilities: List[str] = Field(default_factory=list)
    workflow_id: Optional[UUID] = None
    input_artifacts: Dict[str, Any] = Field(default_factory=dict)
    dependencies: List[UUID] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    """Request to update a task."""

    state: Optional[str] = None
    agent_id: Optional[UUID] = None
    output_artifacts: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class TaskResponse(BaseModel):
    """Response with task details."""

    id: UUID
    name: str
    description: str
    state: str
    agent_id: Optional[UUID] = None
    priority: int
    queued_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Project Schemas
# ============================================================================


class ProjectCreate(BaseModel):
    """Request to create a project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    default_provider_id: Optional[UUID] = None


class ProjectResponse(BaseModel):
    """Response with project details."""

    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Workflow Schemas
# ============================================================================


class WorkflowCreate(BaseModel):
    """Request to create a workflow."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    project_id: UUID
    dag_definition: Dict[str, Any]
    execution_parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowUpdate(BaseModel):
    """Request to update a workflow."""

    state: Optional[str] = None
    execution_parameters: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Response with workflow details."""

    id: UUID
    name: str
    description: Optional[str]
    state: str
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# Event Schemas
# ============================================================================


class EventResponse(BaseModel):
    """Response with event details."""

    id: UUID
    timestamp: datetime
    event_type: str
    severity: str
    message: Optional[str]
    data: Dict[str, Any]

    class Config:
        from_attributes = True


# ============================================================================
# Message Schemas
# ============================================================================


class MessagePublish(BaseModel):
    """Request to publish a message."""

    topic: str
    payload: Dict[str, Any]
    message_type: str = "custom"
    recipient_agent_ids: Optional[List[UUID]] = None


class MessageResponse(BaseModel):
    """Response for published message."""

    id: UUID
    timestamp: datetime
    topic: str
    delivery_status: str
    subscribers_count: int


# ============================================================================
# Provider Schemas
# ============================================================================


class ProviderConfigResponse(BaseModel):
    """Response with provider config details."""

    id: UUID
    name: str
    provider_type: str
    enabled: bool
    model_catalog: List[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Error Schemas
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# Pagination
# ============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================================================
# List Responses
# ============================================================================


class ListResponse(BaseModel):
    """Generic list response wrapper."""

    items: List[Any]
    total: int
    limit: int
    offset: int

    @property
    def page_count(self) -> int:
        """Calculate total number of pages."""
        if self.limit == 0:
            return 0
        return (self.total + self.limit - 1) // self.limit

    @property
    def current_page(self) -> int:
        """Calculate current page number."""
        if self.limit == 0:
            return 1
        return (self.offset // self.limit) + 1
