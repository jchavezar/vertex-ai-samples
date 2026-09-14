"""Hybrid Live Audio + Text ADK Agent with Gemini 2.5 Live Handoff Fix (GitHub #5238).

This module provides `HybridLiveTextGemini`, a drop-in subclass of `google.adk.models.google_llm.Gemini`
that resolves the `transfer_to_agent` sub-agent silence bug on `gemini-live-2.5-flash-native-audio`
across all ADK versions (including 2.7.1, 2.8.0, and 2.9.0) while supporting both:
1. Live Bidirectional Audio streaming (`bidi_stream_query` / `run_live`)
2. Standard Text streaming (`stream_query` / `async_stream_query`)
"""

from contextlib import asynccontextmanager
from datetime import datetime
from functools import cached_property
import json
import os
from typing import AsyncGenerator

import certifi
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import FunctionTool
from google.genai import Client
from google.genai import types

# Force certifi CA bundle to prevent SSLCertVerificationError on WebSockets
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


class HybridLiveTextGemini(Gemini):
  """Hybrid Gemini model wrapper supporting Live Audio WebSockets + Text Generation.

  Fixes GitHub Issue #5238 (`transfer_to_agent` silence on `gemini-live-2.5-flash-native-audio`)
  by wrapping `connection.send_history` inside `connect()` to inject a realtime wakeup signal
  (`send_realtime_input(text='.')`) whenever `turn_complete=True`.
  """

  text_model: str = "gemini-2.5-flash"
  enable_handoff_wakeup_fix: bool = True

  def __getstate__(self):
    """Strip unpicklable thread lock/SSL client properties before cloudpickle serialization."""
    state = self.__dict__.copy()
    state.pop("api_client", None)
    state.pop("_live_api_client", None)
    return state

  @cached_property
  def api_client(self) -> Client:
    return Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )

  @cached_property
  def _live_api_client(self) -> Client:
    return Client(
        vertexai=True,
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        http_options=types.HttpOptions(api_version="v1beta1"),
    )

  async def generate_content_async(
      self, llm_request: LlmRequest, stream: bool = False
  ) -> AsyncGenerator[LlmResponse, None]:
    """Routes standard text queries (`stream_query`) to `self.text_model` (`gemini-2.5-flash`)."""
    original_model = self.model
    original_Request_model = llm_request.model
    try:
      self.model = self.text_model
      llm_request.model = self.text_model
      if llm_request.config and llm_request.config.response_modalities:
        llm_request.config.response_modalities = ["TEXT"]
      async for response in super().generate_content_async(
          llm_request, stream=stream
      ):
        yield response
    finally:
      self.model = original_model
      llm_request.model = original_Request_model

  @asynccontextmanager
  async def connect(self, llm_request: LlmRequest):
    """Establishes Gemini Live WebSocket connection with optional post-transfer wakeup fix."""
    async with super().connect(llm_request) as connection:
      if self.enable_handoff_wakeup_fix:
        orig_send_history = connection.send_history

        async def _send_history_with_wakeup(history):
          await orig_send_history(history)
          # After send_history sends historical turns on agent transfer,
          # gemini-live-2.5-flash-native-audio requires an explicit realtime input
          # trigger to begin synthesizing the sub-agent's response.
          if getattr(connection, "_gemini_session", None) is not None:
            await connection._gemini_session.send_realtime_input(text=".")

        connection.send_history = _send_history_with_wakeup
      yield connection


# =====================================================================
# Tools & Multi-Agent Definitions
# =====================================================================


def get_current_time() -> str:
  """Get the current date and time in UTC."""
  return json.dumps({"time": datetime.now().isoformat(), "timezone": "UTC"})


def get_weather(city: str = "Miami") -> str:
  """Get the current weather for a city."""
  return json.dumps({
      "city": city,
      "temperature": "75F",
      "condition": "Sunny",
      "humidity": "60%",
  })


def create_agent_hierarchy(enable_fix: bool = True) -> Agent:
  """Creates the root_agent and helper_agent hierarchy.

  Args:
    enable_fix: If True, enables the `_send_history_with_wakeup` fix for #5238.
      If False, reproduces the standard ADK 2.7.1 bug.
  """
  helper_llm = HybridLiveTextGemini(
      model="gemini-live-2.5-flash-native-audio",
      text_model="gemini-2.5-flash",
      enable_handoff_wakeup_fix=enable_fix,
  )
  root_llm = HybridLiveTextGemini(
      model="gemini-live-2.5-flash-native-audio",
      text_model="gemini-2.5-flash",
      enable_handoff_wakeup_fix=enable_fix,
  )

  helper_agent = Agent(
      name="helper_agent",
      model=helper_llm,
      description=(
          "Helper agent that answers questions about current time and weather."
      ),
      instruction=(
          "You are a helpful specialist agent. Use get_current_time or"
          " get_weather to answer user questions concisely and clearly."
      ),
      tools=[
          FunctionTool(get_current_time),
          FunctionTool(get_weather),
      ],
  )

  root_agent = Agent(
      name="root_agent",
      model=root_llm,
      description="Root receptionist agent that routes to helper_agent.",
      instruction=(
          "You are the receptionist agent. For any questions about time or"
          " weather, immediately transfer to 'helper_agent' using"
          " transfer_to_agent."
      ),
      sub_agents=[helper_agent],
  )
  return root_agent


# Default export for ADK CLI / Agent Engine
root_agent = create_agent_hierarchy(enable_fix=True)
