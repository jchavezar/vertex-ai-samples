import concurrent.futures
import contextlib
import json
import os
import time
from datetime import datetime
from functools import cached_property
import certifi

os.environ.setdefault("SSL_CERT_FILE", certifi.where())
os.environ.setdefault("REQUESTS_CA_BUNDLE", certifi.where())

import vertexai
from vertexai import types as vertexai_types
from vertexai.preview.reasoning_engines.templates.adk import AdkApp
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import FunctionTool
from google.genai import Client, types
from google.genai.types import GenerateContentConfig

PROJECT_ID = "vtxdemos"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://adk_staging_bucket_vtxdemos"


def get_current_time() -> str:
    """Get the current date and time."""
    return json.dumps({"time": datetime.now().isoformat(), "timezone": "UTC"})


def get_weather(city: str = "Miami") -> str:
    """Get the current weather for a city."""
    return json.dumps({
        "city": city,
        "temperature": "75F",
        "condition": "Sunny",
        "humidity": "60%",
    })


# =====================================================================
# 1. BUGGY MODEL CLASS (Reproduces customer issue on google-adk 2.7.1)
# =====================================================================
class BuggyHybridLiveTextGemini(Gemini):
    """Unpatched Live+Text model reproducing GitHub issue #5238 on ADK 2.7.1."""

    model: str = "gemini-live-2.5-flash-native-audio"
    text_model: str = "gemini-2.5-flash"

    def __getstate__(self):
        state = super().__getstate__()
        if isinstance(state, dict) and "__dict__" in state:
            state["__dict__"] = {
                k: v
                for k, v in state["__dict__"].items()
                if k not in ("api_client", "_live_api_client")
            }
        return state

    @cached_property
    def api_client(self) -> Client:
        return Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", PROJECT_ID),
            location="global",
            http_options=types.HttpOptions(headers=self._tracking_headers()),
        )

    @cached_property
    def _live_api_client(self) -> Client:
        return Client(
            vertexai=True,
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", PROJECT_ID),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", LOCATION),
            http_options=types.HttpOptions(
                headers=self._tracking_headers(),
                api_version=self._live_api_version,
            ),
        )

    async def generate_content_async(self, llm_request, stream: bool = False):
        llm_request.model = self.text_model
        if llm_request.config:
            llm_request.config.thinking_config = types.ThinkingConfig(thinking_budget=0)
        async for resp in super().generate_content_async(llm_request, stream=stream):
            yield resp


# =====================================================================
# 2. FIXED MODEL CLASS (Includes post-transfer wakeup trigger patch)
# =====================================================================
class FixedHybridLiveTextGemini(BuggyHybridLiveTextGemini):
    """Patched Live+Text model that sends '.' wakeup trigger after transfer_to_agent handoff."""

    @contextlib.asynccontextmanager
    async def connect(self, llm_request):
        async with super().connect(llm_request) as connection:
            orig_send_history = connection.send_history

            async def _send_history_with_wakeup(history):
                connection._is_gemini_3_x_live = False
                await orig_send_history(history)
                if history and getattr(history[-1], "role", None) == "user":
                    await connection._gemini_session.send_realtime_input(text=".")

            connection.send_history = _send_history_with_wakeup
            yield connection


# Build Buggy Agent Hierarchy
buggy_helper = Agent(
    model=BuggyHybridLiveTextGemini(),
    name="helper_agent",
    description="Handles weather and travel queries.",
    instruction=(
        "You are a helpful weather assistant. "
        "When the user asks about weather, call get_weather and respond. "
        "If the user asks about ANYTHING other than weather or travel, "
        "you MUST immediately transfer back to root_agent. "
        "Do NOT answer non-weather questions yourself."
    ),
    tools=[FunctionTool(get_weather)],
    generate_content_config=GenerateContentConfig(temperature=0.0),
)

buggy_root = Agent(
    model=BuggyHybridLiveTextGemini(),
    name="root_agent",
    description="Main coordinator. Delegates weather to helper_agent.",
    instruction=(
        "You are a concierge assistant. "
        "When the user asks about weather or travel, transfer to helper_agent. "
        "For all other questions, answer directly. "
        "Keep responses brief (1-2 sentences)."
    ),
    sub_agents=[buggy_helper],
    tools=[FunctionTool(get_current_time)],
    generate_content_config=GenerateContentConfig(temperature=0.0),
)

# Build Fixed Agent Hierarchy
fixed_helper = Agent(
    model=FixedHybridLiveTextGemini(),
    name="helper_agent",
    description="Handles weather and travel queries.",
    instruction=(
        "You are a helpful weather assistant. "
        "When the user asks about weather, call get_weather and respond. "
        "If the user asks about ANYTHING other than weather or travel, "
        "you MUST immediately transfer back to root_agent. "
        "Do NOT answer non-weather questions yourself."
    ),
    tools=[FunctionTool(get_weather)],
    generate_content_config=GenerateContentConfig(temperature=0.0),
)

fixed_root = Agent(
    model=FixedHybridLiveTextGemini(),
    name="root_agent",
    description="Main coordinator. Delegates weather to helper_agent.",
    instruction=(
        "You are a concierge assistant. "
        "When the user asks about weather or travel, transfer to helper_agent. "
        "For all other questions, answer directly. "
        "Keep responses brief (1-2 sentences)."
    ),
    sub_agents=[fixed_helper],
    tools=[FunctionTool(get_current_time)],
    generate_content_config=GenerateContentConfig(temperature=0.0),
)


def deploy_instance(name_label: str, agent_obj: Agent, requirements: list[str]):
    print(f"[{name_label}] Starting deployment to Vertex AI Agent Engine...")
    start_t = time.time()
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    adk_app = AdkApp(agent=agent_obj)
    remote = client.agent_engines.create(
        agent=adk_app,
        config=vertexai_types.AgentEngineConfig(
            display_name=name_label,
            staging_bucket=STAGING_BUCKET,
            requirements=requirements,
            agent_server_mode=vertexai_types.AgentServerMode.EXPERIMENTAL,
        ),
    )
    elapsed = time.time() - start_t
    res_name = remote.api_resource.name
    print(f"[{name_label}] ✅ Deployed in {elapsed:.1f}s -> {res_name}")
    return res_name


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f_buggy = executor.submit(
            deploy_instance,
            "adk-live-buggy-2-7-1",
            buggy_root,
            [
                "google-adk==2.7.1",
                "google-cloud-aiplatform[adk,agent_engines]>=1.147.0",
                "pydantic",
                "cloudpickle",
                "certifi",
                "python-dotenv",
            ],
        )
        f_fixed = executor.submit(
            deploy_instance,
            "adk-live-fixed-2-7-1",
            fixed_root,
            [
                "google-adk==2.7.1",
                "google-cloud-aiplatform[adk,agent_engines]>=1.147.0",
                "pydantic",
                "cloudpickle",
                "certifi",
                "python-dotenv",
            ],
        )

        buggy_res = f_buggy.result()
        fixed_res = f_fixed.result()

    print("\n" + "=" * 70)
    print("BOTH AGENT RUNTIMES DEPLOYED SUCCESSFULLY!")
    print(f"1. Buggy Runtime (ADK 2.7.1 unpatched): {buggy_res}")
    print(f"2. Fixed Runtime (ADK latest + trigger): {fixed_res}")
    print("=" * 70)
