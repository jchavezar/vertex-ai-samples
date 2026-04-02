"""Model provider abstraction for multi-model support."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
import json
import httpx

import vertexai
import google.auth
import google.auth.transport.requests
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Content, Part
from langchain_google_vertexai import ChatVertexAI
from langchain_anthropic import ChatAnthropic

import logging

logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    """Abstract base class for model providers."""

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate a response from the model."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream a response from the model."""
        pass

    @abstractmethod
    def get_langchain_model(self) -> Any:
        """Get LangChain-compatible model for LangGraph."""
        pass

    @abstractmethod
    def get_adk_model_string(self) -> str:
        """Get model string for ADK."""
        pass


class VertexProvider(ModelProvider):
    """Provider for Vertex AI managed models (Gemini)."""

    def __init__(
        self,
        model_id: str,
        project_id: str,
        location: str = "us-central1",
        **config: Any,
    ) -> None:
        self.model_id = model_id
        self.project_id = project_id
        self.location = location
        self.config = config

        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self._model = GenerativeModel(model_id)
        self._langchain_model = ChatVertexAI(
            model=model_id,
            project=project_id,
            location=location,
            **config,
        )

        logger.info(f"Vertex provider initialized: {model_id}")

    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate using Vertex AI Gemini."""
        # Convert messages to Vertex AI format
        contents = self._convert_messages(messages)

        generation_config = {
            "max_output_tokens": kwargs.get("max_tokens", 8192),
            "temperature": kwargs.get("temperature", 0.7),
        }

        response = await self._model.generate_content_async(
            contents,
            generation_config=generation_config,
        )

        return {
            "content": response.text,
            "usage": {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
            },
            "model": self.model_id,
        }

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream using Vertex AI Gemini."""
        contents = self._convert_messages(messages)

        response = await self._model.generate_content_async(
            contents,
            stream=True,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    def _convert_messages(self, messages: list[dict[str, Any]]) -> list[Content]:
        """Convert standard messages to Vertex AI Content format."""
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(Content(role=role, parts=[Part.from_text(msg["content"])]))
        return contents

    def get_langchain_model(self) -> ChatVertexAI:
        """Get LangChain ChatVertexAI model."""
        return self._langchain_model

    def get_adk_model_string(self) -> str:
        """Get ADK model string - native Vertex AI models use direct model name."""
        return self.model_id


class ClaudeVertexProvider(ModelProvider):
    """Provider for Claude models via Vertex AI using AnthropicVertex SDK."""

    def __init__(
        self,
        model_id: str,
        project_id: str,
        location: str = "global",  # Claude uses global endpoint
        **config: Any,
    ) -> None:
        from anthropic import AnthropicVertex, AsyncAnthropicVertex

        self.model_id = model_id
        self.project_id = project_id
        self.location = location
        self.config = config

        # Initialize sync and async clients
        self._client = AnthropicVertex(region=location, project_id=project_id)
        self._async_client = AsyncAnthropicVertex(region=location, project_id=project_id)

        logger.info(f"Claude Vertex provider initialized: {model_id} (region={location})")

    def _convert_messages(self, messages: list[dict[str, Any]]) -> list[dict]:
        """Convert messages to Anthropic format."""
        result = []
        for msg in messages:
            content = msg.get("content", "")
            result.append({
                "role": msg["role"],
                "content": content,
            })
        return result

    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate using Claude via Vertex AI."""
        params = {
            "model": self.model_id,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": self._convert_messages(messages),
        }

        if kwargs.get("temperature") is not None:
            params["temperature"] = kwargs["temperature"]

        if kwargs.get("system"):
            params["system"] = kwargs["system"]

        response = await self._async_client.messages.create(**params)

        return {
            "content": response.content[0].text,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "model": self.model_id,
        }

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream using Claude via Vertex AI."""
        params = {
            "model": self.model_id,
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": self._convert_messages(messages),
        }

        if kwargs.get("temperature") is not None:
            params["temperature"] = kwargs["temperature"]

        async with self._async_client.messages.stream(**params) as stream:
            async for text in stream.text_stream:
                yield text

    def get_langchain_model(self) -> Any:
        """Get LangChain model for LangGraph."""
        from langchain_anthropic import ChatAnthropicVertex
        return ChatAnthropicVertex(
            model=self.model_id,
            project=self.project_id,
            region=self.location,
        )

    def get_adk_model_string(self) -> str:
        """Get ADK model string - Claude models need special handling."""
        return f"claude-vertex/{self.model_id}"


class LlamaVertexProvider(ModelProvider):
    """Provider for Llama models via Vertex AI Model Garden MaaS."""

    def __init__(
        self,
        model_id: str,
        project_id: str,
        location: str = "us-central1",
        **config: Any,
    ) -> None:
        self.model_id = model_id
        self.project_id = project_id
        self.location = location
        self.config = config
        self._http_client = httpx.AsyncClient(timeout=120.0)

        logger.info(f"Llama Vertex provider initialized: {model_id} (location={location})")

    def _get_credentials(self):
        """Get and refresh Google credentials."""
        credentials, _ = google.auth.default()
        auth_req = google.auth.transport.requests.Request()
        credentials.refresh(auth_req)
        return credentials

    def _get_endpoint(self) -> str:
        """Get the Vertex AI endpoint for Llama."""
        return f"https://{self.location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/meta/models/{self.model_id}:generateContent"

    def _convert_messages(self, messages: list[dict[str, Any]]) -> list[dict]:
        """Convert messages to Vertex AI format."""
        result = []
        for msg in messages:
            content = msg.get("content", "")
            result.append({
                "role": msg["role"],
                "parts": [{"text": content}]
            })
        return result

    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate using Llama via Vertex AI."""
        credentials = self._get_credentials()

        payload = {
            "contents": self._convert_messages(messages),
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            }
        }

        if kwargs.get("temperature") is not None:
            payload["generationConfig"]["temperature"] = kwargs["temperature"]

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        response = await self._http_client.post(
            self._get_endpoint(),
            headers=headers,
            json=payload,
        )
        response.raise_for_status()
        result = response.json()

        text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        return {
            "content": text,
            "usage": result.get("usageMetadata", {}),
            "model": self.model_id,
        }

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream using Llama via Vertex AI."""
        credentials = self._get_credentials()

        payload = {
            "contents": self._convert_messages(messages),
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", 4096),
            }
        }

        headers = {
            "Authorization": f"Bearer {credentials.token}",
            "Content-Type": "application/json",
        }

        endpoint = self._get_endpoint().replace(":generateContent", ":streamGenerateContent")

        async with self._http_client.stream(
            "POST",
            endpoint,
            headers=headers,
            json=payload,
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.strip():
                    try:
                        data = json.loads(line.lstrip("[,"))
                        text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                        if text:
                            yield text
                    except json.JSONDecodeError:
                        pass

    def get_langchain_model(self) -> Any:
        """Get LangChain model for LangGraph."""
        return ChatVertexAI(
            model=f"publishers/meta/models/{self.model_id}",
            project=self.project_id,
            location=self.location,
        )

    def get_adk_model_string(self) -> str:
        """Get ADK model string."""
        return f"llama-vertex/{self.model_id}"


class ModelGardenProvider(ModelProvider):
    """Provider for other Model Garden models (Mistral, etc.)."""

    def __init__(
        self,
        model_id: str,
        project_id: str,
        location: str = "us-central1",
        **config: Any,
    ) -> None:
        self.model_id = model_id
        self.project_id = project_id
        self.location = location
        self.config = config

        self._langchain_model = ChatVertexAI(
            model=model_id,
            project=project_id,
            location=location,
            **config,
        )

        logger.info(f"Model Garden provider initialized: {model_id}")

    async def generate(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate using Model Garden model."""
        response = await self._langchain_model.ainvoke(
            messages,
            **kwargs,
        )

        return {
            "content": response.content,
            "usage": response.usage_metadata if hasattr(response, "usage_metadata") else {},
            "model": self.model_id,
        }

    async def stream(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """Stream using Model Garden model."""
        async for chunk in self._langchain_model.astream(messages, **kwargs):
            if chunk.content:
                yield chunk.content

    def get_langchain_model(self) -> Any:
        """Get LangChain model."""
        return self._langchain_model

    def get_adk_model_string(self) -> str:
        """Get ADK model string for Model Garden."""
        return f"vertexai/{self.model_id}"
