"""Factory for creating model providers."""

from typing import Any

from models.provider import ModelProvider, VertexProvider, ModelGardenProvider, ClaudeVertexProvider, LlamaVertexProvider
from core.config import get_settings
from core.registry import ModelRegistry, ModelInfo

import logging

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating model providers based on configuration."""

    def __init__(self, model_registry: ModelRegistry) -> None:
        self.model_registry = model_registry
        self._settings = get_settings()
        self._providers: dict[str, ModelProvider] = {}

    def get_provider(self, model_id: str) -> ModelProvider:
        """Get or create a model provider for the given model ID."""
        if model_id in self._providers:
            return self._providers[model_id]

        model_info = self.model_registry.get(model_id)
        if not model_info:
            raise ValueError(f"Model '{model_id}' not found in registry")

        provider = self._create_provider(model_info)
        self._providers[model_id] = provider
        return provider

    def _create_provider(self, model_info: ModelInfo) -> ModelProvider:
        """Create a provider based on model info."""
        if model_info.provider == "vertex":
            return VertexProvider(
                model_id=model_info.model_id,
                project_id=self._settings.gcp_project_id,
                location=self._settings.gcp_location,
                **model_info.config,
            )
        elif model_info.provider == "claude_vertex":
            # Claude models via Vertex AI rawPredict (global endpoint)
            return ClaudeVertexProvider(
                model_id=model_info.model_id,
                project_id=self._settings.gcp_project_id,
                location="global",
                **model_info.config,
            )
        elif model_info.provider == "llama_vertex":
            # Llama models via Vertex AI MaaS
            return LlamaVertexProvider(
                model_id=model_info.model_id,
                project_id=self._settings.gcp_project_id,
                location="us-central1",
                **model_info.config,
            )
        elif model_info.provider == "model_garden":
            return ModelGardenProvider(
                model_id=model_info.model_id,
                project_id=self._settings.gcp_project_id,
                location=self._settings.gcp_location,
                **model_info.config,
            )
        else:
            raise ValueError(f"Unsupported provider: {model_info.provider}")

    def register_custom_model(
        self,
        model_id: str,
        provider: str,
        display_name: str,
        **config: Any,
    ) -> ModelInfo:
        """Register a custom model."""
        model_info = ModelInfo(
            model_id=model_id,
            provider=provider,
            display_name=display_name,
            config=config,
        )
        self.model_registry.register(model_info)
        return model_info
