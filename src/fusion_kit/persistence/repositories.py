"""
Repository layer for async CRUD operations on all models.

Provides async database access patterns for agents, tasks, workflows, and other entities.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fusion_kit.persistence.models import (
    Agent,
    Capability,
    Event,
    Message,
    Project,
    ProviderConfig,
    ResourceMetrics,
    Task,
    Workflow,
    Workspace,
)


# ============================================================================
# Base Repository
# ============================================================================


class BaseRepository:
    """Base repository class with common CRUD operations."""

    def __init__(self, session: AsyncSession, model_class):
        self.session = session
        self.model_class = model_class

    async def create(self, **kwargs) -> object:
        """Create and return a new instance."""
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: UUID) -> Optional[object]:
        """Get instance by ID."""
        stmt = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[object]:
        """Get all instances with pagination."""
        stmt = select(self.model_class).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, id: UUID, **kwargs) -> Optional[object]:
        """Update instance by ID."""
        instance = await self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            await self.session.flush()
        return instance

    async def delete(self, id: UUID) -> bool:
        """Delete instance by ID."""
        instance = await self.get_by_id(id)
        if instance:
            await self.session.delete(instance)
            await self.session.flush()
            return True
        return False


# ============================================================================
# Agent Repository
# ============================================================================


class AgentRepository(BaseRepository):
    """Repository for Agent model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Agent)

    async def get_by_project(self, project_id: UUID) -> List[Agent]:
        """Get all agents for a project."""
        stmt = select(Agent).where(Agent.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_state(self, state: str) -> List[Agent]:
        """Get agents by state."""
        stmt = select(Agent).where(Agent.state == state)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_relationships(self, id: UUID) -> Optional[Agent]:
        """Get agent with all relationships loaded."""
        stmt = (
            select(Agent)
            .where(Agent.id == id)
            .options(
                selectinload(Agent.project),
                selectinload(Agent.provider_config),
                selectinload(Agent.tasks),
                selectinload(Agent.metrics),
            )
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


# ============================================================================
# Task Repository
# ============================================================================


class TaskRepository(BaseRepository):
    """Repository for Task model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Task)

    async def get_by_agent(self, agent_id: UUID) -> List[Task]:
        """Get all tasks for an agent."""
        stmt = select(Task).where(Task.agent_id == agent_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_workflow(self, workflow_id: UUID) -> List[Task]:
        """Get all tasks in a workflow."""
        stmt = select(Task).where(Task.workflow_id == workflow_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_state(self, state: str) -> List[Task]:
        """Get tasks by state."""
        stmt = select(Task).where(Task.state == state)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_queued_tasks(self, limit: int = 10) -> List[Task]:
        """Get queued tasks ordered by priority."""
        stmt = (
            select(Task)
            .where(Task.state == "queued")
            .order_by(Task.priority.desc(), Task.queued_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# Workspace Repository
# ============================================================================


class WorkspaceRepository(BaseRepository):
    """Repository for Workspace model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Workspace)

    async def get_by_agent(self, agent_id: UUID) -> Optional[Workspace]:
        """Get workspace for an agent."""
        stmt = select(Workspace).where(Workspace.agent_id == agent_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_root_path(self, root_path: str) -> Optional[Workspace]:
        """Get workspace by root path."""
        stmt = select(Workspace).where(Workspace.root_path == root_path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


# ============================================================================
# Workflow Repository
# ============================================================================


class WorkflowRepository(BaseRepository):
    """Repository for Workflow model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Workflow)

    async def get_by_project(self, project_id: UUID) -> List[Workflow]:
        """Get all workflows for a project."""
        stmt = select(Workflow).where(Workflow.project_id == project_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_state(self, state: str) -> List[Workflow]:
        """Get workflows by state."""
        stmt = select(Workflow).where(Workflow.state == state)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_with_tasks(self, id: UUID) -> Optional[Workflow]:
        """Get workflow with all tasks loaded."""
        stmt = select(Workflow).where(Workflow.id == id).options(selectinload(Workflow.tasks))
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


# ============================================================================
# Event Repository
# ============================================================================


class EventRepository(BaseRepository):
    """Repository for Event model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Event)

    async def get_by_agent(self, agent_id: UUID, limit: int = 100) -> List[Event]:
        """Get events for an agent."""
        stmt = (
            select(Event)
            .where(Event.source_agent_id == agent_id)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_type(self, event_type: str, limit: int = 100) -> List[Event]:
        """Get events by type."""
        stmt = (
            select(Event)
            .where(Event.event_type == event_type)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_severity(self, severity: str, limit: int = 100) -> List[Event]:
        """Get events by severity."""
        stmt = (
            select(Event)
            .where(Event.severity == severity)
            .order_by(Event.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_recent(self, limit: int = 100) -> List[Event]:
        """Get recent events."""
        stmt = select(Event).order_by(Event.timestamp.desc()).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# Message Repository
# ============================================================================


class MessageRepository(BaseRepository):
    """Repository for Message model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Message)

    async def get_by_sender(self, sender_agent_id: UUID) -> List[Message]:
        """Get messages from a sender."""
        stmt = select(Message).where(Message.sender_agent_id == sender_agent_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_topic(self, topic: str, limit: int = 100) -> List[Message]:
        """Get messages from a topic."""
        stmt = (
            select(Message)
            .where(Message.topic == topic)
            .order_by(Message.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_status(self, status: str) -> List[Message]:
        """Get messages by delivery status."""
        stmt = select(Message).where(Message.delivery_status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# Capability Repository
# ============================================================================


class CapabilityRepository(BaseRepository):
    """Repository for Capability model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Capability)

    async def get_by_name(self, name: str) -> Optional[Capability]:
        """Get capability by name."""
        stmt = select(Capability).where(Capability.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_category(self, category: str) -> List[Capability]:
        """Get capabilities by category."""
        stmt = select(Capability).where(Capability.category == category)
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# Project Repository
# ============================================================================


class ProjectRepository(BaseRepository):
    """Repository for Project model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        stmt = select(Project).where(Project.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_agents(self, id: UUID) -> Optional[Project]:
        """Get project with all agents loaded."""
        stmt = (
            select(Project)
            .where(Project.id == id)
            .options(selectinload(Project.agents), selectinload(Project.workflows))
        )
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()


# ============================================================================
# ResourceMetrics Repository
# ============================================================================


class ResourceMetricsRepository(BaseRepository):
    """Repository for ResourceMetrics model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ResourceMetrics)

    async def get_by_agent(self, agent_id: UUID, limit: int = 100) -> List[ResourceMetrics]:
        """Get metrics for an agent."""
        stmt = (
            select(ResourceMetrics)
            .where(ResourceMetrics.agent_id == agent_id)
            .order_by(ResourceMetrics.timestamp.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# ProviderConfig Repository
# ============================================================================


class ProviderConfigRepository(BaseRepository):
    """Repository for ProviderConfig model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session, ProviderConfig)

    async def get_by_name(self, name: str) -> Optional[ProviderConfig]:
        """Get provider config by name."""
        stmt = select(ProviderConfig).where(ProviderConfig.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_enabled(self) -> List[ProviderConfig]:
        """Get all enabled providers."""
        stmt = select(ProviderConfig).where(ProviderConfig.enabled == True)
        result = await self.session.execute(stmt)
        return result.scalars().all()


# ============================================================================
# Unit of Work Pattern
# ============================================================================


class UnitOfWork:
    """
    Unit of work pattern for managing all repositories and transactions.

    Usage:
        async with UnitOfWork(session) as uow:
            agent = await uow.agents.get_by_id(id)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.agents = AgentRepository(session)
        self.tasks = TaskRepository(session)
        self.workspaces = WorkspaceRepository(session)
        self.workflows = WorkflowRepository(session)
        self.events = EventRepository(session)
        self.messages = MessageRepository(session)
        self.capabilities = CapabilityRepository(session)
        self.projects = ProjectRepository(session)
        self.metrics = ResourceMetricsRepository(session)
        self.providers = ProviderConfigRepository(session)

    async def commit(self):
        """Commit the transaction."""
        await self.session.commit()

    async def rollback(self):
        """Rollback the transaction."""
        await self.session.rollback()

    async def close(self):
        """Close the session."""
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self.close()
