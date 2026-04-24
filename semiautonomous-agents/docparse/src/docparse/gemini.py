from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel

PROJECT = os.environ.get("DOCPARSE_PROJECT", "my-project")
LOCATION = os.environ.get("DOCPARSE_LOCATION", "global")
LITE_MODEL = os.environ.get("DOCPARSE_LITE", "gemini-3.1-flash-lite-preview")
FLASH_MODEL = os.environ.get("DOCPARSE_FLASH", "gemini-3-flash-preview")
PRO_MODEL = os.environ.get("DOCPARSE_PRO", "gemini-3.1-pro-preview")

_client: genai.Client | None = None


def client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    return _client


def _schema_from_pydantic(model: type[BaseModel]) -> dict:
    schema = model.model_json_schema()
    return _strip_unsupported(schema)


def _strip_unsupported(node: Any) -> Any:
    """Recursively strip JSON-Schema keywords Gemini's responseSchema rejects."""
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            if k in {"$defs", "definitions", "title", "additionalProperties"}:
                continue
            if k == "$ref":
                # Resolve simple local refs by leaving them out -- caller flattens.
                continue
            out[k] = _strip_unsupported(v)
        return out
    if isinstance(node, list):
        return [_strip_unsupported(x) for x in node]
    return node


def _flatten_refs(schema: dict) -> dict:
    """Inline $defs into a self-contained schema so Gemini accepts it."""
    defs = schema.get("$defs") or schema.get("definitions") or {}

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node and node["$ref"].startswith("#/$defs/"):
                key = node["$ref"].split("/")[-1]
                return resolve(defs[key])
            return {k: resolve(v) for k, v in node.items() if k not in {"$defs", "definitions"}}
        if isinstance(node, list):
            return [resolve(x) for x in node]
        return node

    return resolve(schema)


async def warm_up() -> None:
    """One-shot client warm-up: pays the auth/discovery/metadata-server cost
    explicitly at startup instead of on the first random request.

    Past sessions documented 18-20s "cold start" when the genai client
    initializes lazily under concurrent load. Calling this once before fan-out
    converts that hidden tax into a deterministic ~1-2s startup."""
    try:
        await asyncio.wait_for(
            client().aio.models.generate_content(
                model=LITE_MODEL,
                contents="ok",
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=4,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                ),
            ),
            timeout=20.0,
        )
    except Exception:  # noqa: BLE001
        pass  # warm-up is best-effort; never block the pipeline


async def call_vision(
    *,
    model: str,
    prompt: str,
    image_bytes: bytes,
    response_model: type[BaseModel] | None = None,
    temperature: float = 0.0,
    max_retries: int = 3,
    timeout_s: float = 45.0,
    thinking_budget: int | None = None,
) -> Any:
    """Call Gemini with an image + prompt. Returns parsed model or raw text.

    Each attempt is bounded by `timeout_s`; on TimeoutError we cancel the request
    and try again on a fresh connection. This caps the long-tail latency that the
    flash-preview model occasionally exhibits.

    `thinking_budget`: 0 disables thinking (latency win for non-reasoning calls
    like detect/OCR/captioning). Leave as None to use the model default
    (recommended for chart/diagram extraction where reasoning matters)."""
    parts = [
        types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
        types.Part.from_text(text=prompt),
    ]
    contents = [types.Content(role="user", parts=parts)]
    config: dict = {"temperature": temperature}
    if response_model is not None:
        schema = _flatten_refs(response_model.model_json_schema())
        schema = _strip_unsupported(schema)
        config["response_mime_type"] = "application/json"
        config["response_schema"] = schema
    if thinking_budget is not None:
        config["thinking_config"] = types.ThinkingConfig(thinking_budget=thinking_budget)

    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = await asyncio.wait_for(
                client().aio.models.generate_content(
                    model=model,
                    contents=contents,
                    config=types.GenerateContentConfig(**config),
                ),
                timeout=timeout_s,
            )
            text = resp.text or ""
            if response_model is None:
                return text
            data = json.loads(text)
            return response_model.model_validate(data)
        except asyncio.TimeoutError as e:
            last_err = e
            # No backoff on timeout -- the time has already been spent.
            continue
        except Exception as e:  # noqa: BLE001
            last_err = e
            await asyncio.sleep(0.5 * (2**attempt))
    raise RuntimeError(
        f"Gemini call failed after {max_retries} retries: {type(last_err).__name__}: {last_err!r}"
    )
