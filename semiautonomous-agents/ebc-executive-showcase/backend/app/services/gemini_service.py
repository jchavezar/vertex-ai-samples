import logging
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel
from google import genai
from google.genai import types
from app.config import PROJECT_ID, REGION, MODEL_NAME

logger = logging.getLogger("gemini_service")
T = TypeVar("T", bound=BaseModel)

class GeminiService:
    def __init__(self):
        self.project_id = PROJECT_ID
        self.region = REGION
        self.primary_model = MODEL_NAME
        self.fallback_models = ["gemini-2.5-flash", "gemini-2.5-pro"]
        self._client = None
        self._init_client()

    def _init_client(self):
        try:
            self._client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location=self.region
            )
            logger.info(f"GenAI Client initialized with Vertex AI (project={self.project_id}, region={self.region})")
        except Exception as e:
            logger.error(f"Error initializing GenAI Client: {e}")
            self._client = None

    @property
    def client(self) -> genai.Client:
        if self._client is None:
            self._init_client()
        return self._client

    def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.4
    ) -> str:
        models_to_try = [model_name] if model_name else [self.primary_model] + self.fallback_models
        # eliminate duplicates while preserving order
        dedup_models = []
        for m in models_to_try:
            if m and m not in dedup_models:
                dedup_models.append(m)

        last_error = None
        for m in dedup_models:
            try:
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    system_instruction=system_instruction
                )
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                return response.text or ""
            except Exception as e:
                logger.warning(f"Failed generation with model {m}: {e}")
                last_error = e

        raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

    def generate_structured(
        self,
        prompt: str,
        response_schema: Type[T],
        system_instruction: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: float = 0.2
    ) -> T:
        models_to_try = [model_name] if model_name else [self.primary_model] + self.fallback_models
        dedup_models = []
        for m in models_to_try:
            if m and m not in dedup_models:
                dedup_models.append(m)

        last_error = None
        for m in dedup_models:
            try:
                config = types.GenerateContentConfig(
                    temperature=temperature,
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
                response = self.client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=config
                )
                if response.text:
                    return response_schema.model_validate_json(response.text)
            except Exception as e:
                logger.warning(f"Failed structured generation with model {m}: {e}")
                last_error = e

        raise RuntimeError(f"All Gemini models failed structured generation. Last error: {last_error}")

gemini_service = GeminiService()
