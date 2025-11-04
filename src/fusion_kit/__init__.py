"""
Fusion Kit - Multi-Agent Orchestration Framework

A framework for spawning, coordinating, and managing multiple AI agents
with isolated workspaces, message-based communication, and real-time monitoring.
"""

__version__ = "1.0.0"
__author__ = "Factory"

# Lazy imports to avoid requiring all dependencies at once
def __getattr__(name):
    if name == "app":
        from fusion_kit.api import app
        return app
    elif name == "init_db":
        from fusion_kit.persistence import init_db
        return init_db
    elif name == "Base":
        from fusion_kit.persistence import Base
        return Base
    elif name == "MessageQueue":
        from fusion_kit.messaging import MessageQueue
        return MessageQueue
    elif name == "MessageQueueContext":
        from fusion_kit.messaging import MessageQueueContext
        return MessageQueueContext
    elif name == "LLMProvider":
        from fusion_kit.providers import LLMProvider
        return LLMProvider
    elif name == "ProviderRegistry":
        from fusion_kit.providers import ProviderRegistry
        return ProviderRegistry
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "app",
    "init_db",
    "Base",
    "MessageQueue",
    "MessageQueueContext",
    "LLMProvider",
    "ProviderRegistry",
]