"""
Abstract base class for LLM providers.

Defines the interface that all LLM provider implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


# ============================================================================
# Provider Response Models
# ============================================================================


class AgentSpawnResponse(BaseModel):
    """Response from spawning an agent."""

    agent_id: UUID
    workspace_path: str
    status: str
    model_name: str


class MessageResponse(BaseModel):
    """Response from sending a message to agent."""

    message_id: str
    status: str
    response: Optional[str] = None
    tokens_used: Optional[int] = None


class QuotaInfo(BaseModel):
    """Provider quota and usage information."""

    provider_name: str
    requests_remaining: int
    requests_total: int
    tokens_used: int
    tokens_limit: Optional[int] = None
    rate_limit_reset: Optional[str] = None
    cost_usd: float


# ============================================================================
# Abstract Provider Interface
# ============================================================================


class LLMProvider(ABC):
    """
    Abstract base class for LLM provider implementations.

    All LLM providers (OpenRouter, Anthropic, OpenAI, etc.) must implement
    this interface to ensure consistent behavior across the system.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider."""
        pass

    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of supported model names."""
        pass

    @abstractmethod
    async def spawn_agent(
        self,
        model: str,
        capabilities: List[str],
        agent_id: Optional[UUID] = None,
        system_prompt: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AgentSpawnResponse:
        """
        Spawn an AI agent using this provider.

        Args:
            model: Model name to use (must be in supported_models)
            capabilities: List of capabilities the agent should have
            agent_id: Optional ID for the agent (generates if not provided)
            system_prompt: Optional system prompt for agent
            metadata: Optional metadata for the agent

        Returns:
            AgentSpawnResponse with agent details

        Raises:
            ValueError: If model not supported or invalid arguments
            RuntimeError: If provider communication fails
        """
        pass

    @abstractmethod
    async def send_message(
        self,
        agent_id: UUID,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> MessageResponse:
        """
        Send a message to an agent and get a response.

        Args:
            agent_id: ID of the agent to message
            message: Message to send
            context: Optional context for the message

        Returns:
            MessageResponse with agent's response

        Raises:
            ValueError: If agent_id invalid
            RuntimeError: If provider communication fails
        """
        pass

    @abstractmethod
    async def get_agent_status(self, agent_id: UUID) -> Dict[str, Any]:
        """
        Get current status of an agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Dictionary with agent status information

        Raises:
            ValueError: If agent_id invalid
        """
        pass

    @abstractmethod
    async def terminate_agent(self, agent_id: UUID) -> bool:
        """
        Terminate an agent.

        Args:
            agent_id: ID of the agent to terminate

        Returns:
            True if successful, False otherwise

        Raises:
            ValueError: If agent_id invalid
        """
        pass

    @abstractmethod
    def get_quota_info(self) -> QuotaInfo:
        """
        Get quota and usage information for this provider.

        Returns:
            QuotaInfo with current usage and limits

        Raises:
            RuntimeError: If quota information unavailable
        """
        pass

    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate that provider credentials are valid and working.

        Returns:
            True if credentials are valid, False otherwise
        """
        pass

    @abstractmethod
    async def get_provider_info(self) -> Dict[str, Any]:
        """
        Get information about the provider and its current status.

        Returns:
            Dictionary with provider details (name, version, status, etc.)
        """
        pass


# ============================================================================
# Provider Configuration
# ============================================================================


class ProviderConfig(BaseModel):
    """Configuration for a provider instance."""

    name: str
    provider_type: str  # e.g., "openrouter", "anthropic", "openai"
    api_endpoint: str
    api_key: str
    model_catalog: List[str]
    rate_limits: Dict[str, int] = {}
    metadata: Dict[str, Any] = {}

    class Config:
        # Don't expose api_key in string representations
        fields = {"api_key": {"exclude": True}}


# ============================================================================
# Provider Factory
# ============================================================================


class ProviderFactory:
    """Factory for creating provider instances."""

    _providers: Dict[str, type] = {}

    @classmethod
    def register(cls, provider_type: str, provider_class: type) -> None:
        """
        Register a provider implementation.

        Args:
            provider_type: Type identifier for the provider
            provider_class: Provider class (must inherit from LLMProvider)

        Raises:
            TypeError: If provider_class doesn't inherit from LLMProvider
        """
        if not issubclass(provider_class, LLMProvider):
            raise TypeError(f"{provider_class} must inherit from LLMProvider")
        cls._providers[provider_type] = provider_class

    @classmethod
    def create(cls, provider_type: str, config: ProviderConfig) -> LLMProvider:
        """
        Create a provider instance.

        Args:
            provider_type: Type identifier for the provider
            config: Configuration for the provider

        Returns:
            Provider instance

        Raises:
            ValueError: If provider_type not registered
        """
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}. Registered: {list(cls._providers.keys())}")

        provider_class = cls._providers[provider_type]
        return provider_class(config)

    @classmethod
    def get_registered_providers(cls) -> List[str]:
        """Get list of registered provider types."""
        return list(cls._providers.keys())
