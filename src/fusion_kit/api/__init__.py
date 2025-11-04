"""FastAPI application and endpoints."""

# Lazy imports to avoid requiring fastapi at import time
def __getattr__(name):
    if name == "app":
        from fusion_kit.api.main import app
        return app
    elif name == "HealthCheckResponse":
        from fusion_kit.api.schemas import HealthCheckResponse
        return HealthCheckResponse
    elif name == "AgentCreate":
        from fusion_kit.api.schemas import AgentCreate
        return AgentCreate
    elif name == "AgentUpdate":
        from fusion_kit.api.schemas import AgentUpdate
        return AgentUpdate
    elif name == "AgentResponse":
        from fusion_kit.api.schemas import AgentResponse
        return AgentResponse
    elif name == "TaskCreate":
        from fusion_kit.api.schemas import TaskCreate
        return TaskCreate
    elif name == "TaskUpdate":
        from fusion_kit.api.schemas import TaskUpdate
        return TaskUpdate
    elif name == "TaskResponse":
        from fusion_kit.api.schemas import TaskResponse
        return TaskResponse
    elif name == "ProjectCreate":
        from fusion_kit.api.schemas import ProjectCreate
        return ProjectCreate
    elif name == "ProjectResponse":
        from fusion_kit.api.schemas import ProjectResponse
        return ProjectResponse
    elif name == "WorkflowCreate":
        from fusion_kit.api.schemas import WorkflowCreate
        return WorkflowCreate
    elif name == "WorkflowUpdate":
        from fusion_kit.api.schemas import WorkflowUpdate
        return WorkflowUpdate
    elif name == "WorkflowResponse":
        from fusion_kit.api.schemas import WorkflowResponse
        return WorkflowResponse
    elif name == "EventResponse":
        from fusion_kit.api.schemas import EventResponse
        return EventResponse
    elif name == "MessagePublish":
        from fusion_kit.api.schemas import MessagePublish
        return MessagePublish
    elif name == "MessageResponseSchema":
        from fusion_kit.api.schemas import MessageResponse
        return MessageResponse
    elif name == "ProviderConfigResponse":
        from fusion_kit.api.schemas import ProviderConfigResponse
        return ProviderConfigResponse
    elif name == "ErrorResponse":
        from fusion_kit.api.schemas import ErrorResponse
        return ErrorResponse
    elif name == "PaginationParams":
        from fusion_kit.api.schemas import PaginationParams
        return PaginationParams
    elif name == "ListResponse":
        from fusion_kit.api.schemas import ListResponse
        return ListResponse
    elif name == "ConnectionManager":
        from fusion_kit.api.websockets import ConnectionManager
        return ConnectionManager
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "app",
    "HealthCheckResponse",
    "AgentCreate",
    "AgentUpdate",
    "AgentResponse",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "ProjectCreate",
    "ProjectResponse",
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "EventResponse",
    "MessagePublish",
    "MessageResponseSchema",
    "ProviderConfigResponse",
    "ErrorResponse",
    "PaginationParams",
    "ListResponse",
    "ConnectionManager",
]
