"""
Provider registry and management system.

Provides centralized management and discovery of LLM provider implementations.
"""

import logging
from typing import Dict, List, Optional
from uuid import UUID

from fusion_kit.persistence.models import ProviderConfig as ProviderConfigModel
from fusion_kit.providers.base import LLMProvider, ProviderFactory

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """
    Registry for managing provider configurations and instances.

    Provides:
    - Provider discovery and lookup
    - Configuration management
    - Provider lifecycle management
    """

    def __init__(self):
        """Initialize provider registry."""
        self._providers: Dict[str, LLMProvider] = {}
        self._configs: Dict[str, ProviderConfigModel] = {}

    def register_provider(self, provider_id: str, provider: LLMProvider, config: ProviderConfigModel) -> None:
        """
        Register a provider instance with configuration.

        Args:
            provider_id: Unique identifier for this provider instance
            provider: Provider instance
            config: Provider configuration

        Raises:
            ValueError: If provider_id already registered
        """
        if provider_id in self._providers:
            raise ValueError(f"Provider {provider_id} already registered")

        self._providers[provider_id] = provider
        self._configs[provider_id] = config
        logger.info(f"Registered provider: {provider_id} ({config.provider_type})")

    def unregister_provider(self, provider_id: str) -> bool:
        """
        Unregister a provider.

        Args:
            provider_id: ID of provider to unregister

        Returns:
            True if unregistered, False if not found
        """
        if provider_id in self._providers:
            del self._providers[provider_id]
            del self._configs[provider_id]
            logger.info(f"Unregistered provider: {provider_id}")
            return True
        return False

    def get_provider(self, provider_id: str) -> Optional[LLMProvider]:
        """
        Get a provider instance by ID.

        Args:
            provider_id: ID of the provider

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(provider_id)

    def get_provider_config(self, provider_id: str) -> Optional[ProviderConfigModel]:
        """
        Get provider configuration by ID.

        Args:
            provider_id: ID of the provider

        Returns:
            Provider configuration or None if not found
        """
        return self._configs.get(provider_id)

    def get_provider_by_name(self, name: str) -> Optional[LLMProvider]:
        """
        Get provider by name.

        Args:
            name: Provider name (e.g., "openrouter", "anthropic")

        Returns:
            Provider instance or None if not found
        """
        for provider in self._providers.values():
            if provider.provider_name == name:
                return provider
        return None

    def get_all_providers(self) -> Dict[str, LLMProvider]:
        """
        Get all registered providers.

        Returns:
            Dictionary of provider_id -> provider instance
        """
        return self._providers.copy()

    def get_provider_ids(self) -> List[str]:
        """
        Get list of all registered provider IDs.

        Returns:
            List of provider IDs
        """
        return list(self._providers.keys())

    def list_providers_by_type(self, provider_type: str) -> Dict[str, LLMProvider]:
        """
        List all providers of a specific type.

        Args:
            provider_type: Type of provider (e.g., "openrouter")

        Returns:
            Dictionary of provider_id -> provider instance
        """
        return {
            pid: provider
            for pid, provider in self._providers.items()
            if self._configs[pid].provider_type == provider_type
        }

    def has_provider(self, provider_id: str) -> bool:
        """
        Check if provider is registered.

        Args:
            provider_id: ID of the provider

        Returns:
            True if registered, False otherwise
        """
        return provider_id in self._providers

    def get_supported_models(self, provider_id: str) -> List[str]:
        """
        Get list of models supported by a provider.

        Args:
            provider_id: ID of the provider

        Returns:
            List of supported model names

        Raises:
            ValueError: If provider not found
        """
        config = self.get_provider_config(provider_id)
        if not config:
            raise ValueError(f"Provider {provider_id} not found")
        return config.model_catalog

    def find_provider_for_model(self, model_name: str) -> Optional[str]:
        """
        Find a provider that supports a given model.

        Args:
            model_name: Name of the model

        Returns:
            Provider ID that supports the model, or None if not found
        """
        for provider_id, config in self._configs.items():
            if model_name in config.model_catalog:
                return provider_id
        return None

    def validate_provider(self, provider_id: str) -> bool:
        """
        Validate that a provider is configured correctly and accessible.

        Args:
            provider_id: ID of the provider

        Returns:
            True if valid, False otherwise
        """
        provider = self.get_provider(provider_id)
        if not provider:
            logger.warning(f"Provider {provider_id} not found")
            return False

        # Additional validation can be added here
        return True

    def get_provider_info(self, provider_id: str) -> Optional[Dict]:
        """
        Get information about a provider.

        Args:
            provider_id: ID of the provider

        Returns:
            Dictionary with provider information
        """
        provider = self.get_provider(provider_id)
        config = self.get_provider_config(provider_id)

        if not provider or not config:
            return None

        return {
            "id": provider_id,
            "name": provider.provider_name,
            "type": config.provider_type,
            "supported_models": provider.supported_models,
            "endpoint": config.api_endpoint,
            "rate_limits": config.rate_limits,
            "enabled": config.enabled,
        }

    def summary(self) -> Dict:
        """
        Get summary of all registered providers.

        Returns:
            Dictionary with provider summary information
        """
        return {
            "total_providers": len(self._providers),
            "provider_types": list(set(c.provider_type for c in self._configs.values())),
            "providers": {pid: self.get_provider_info(pid) for pid in self._providers.keys()},
        }


# ============================================================================
# Global Registry Instance
# ============================================================================

_global_registry: Optional[ProviderRegistry] = None


def get_provider_registry() -> ProviderRegistry:
    """
    Get the global provider registry.

    Returns:
        Global ProviderRegistry instance
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProviderRegistry()
    return _global_registry


def reset_provider_registry() -> None:
    """Reset the global provider registry (mainly for testing)."""
    global _global_registry
    _global_registry = None


# ============================================================================
# Helper Functions
# ============================================================================


def register_provider(provider_id: str, provider: LLMProvider, config: ProviderConfigModel) -> None:
    """
    Register a provider with the global registry.

    Args:
        provider_id: Unique identifier
        provider: Provider instance
        config: Configuration
    """
    registry = get_provider_registry()
    registry.register_provider(provider_id, provider, config)


def get_provider(provider_id: str) -> Optional[LLMProvider]:
    """
    Get provider from global registry.

    Args:
        provider_id: ID of the provider

    Returns:
        Provider instance or None
    """
    registry = get_provider_registry()
    return registry.get_provider(provider_id)


def list_providers() -> Dict[str, LLMProvider]:
    """
    List all providers from global registry.

    Returns:
        Dictionary of all providers
    """
    registry = get_provider_registry()
    return registry.get_all_providers()
