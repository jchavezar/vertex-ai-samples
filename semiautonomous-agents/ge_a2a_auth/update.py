"""Update the existing Agent Runtime engine in place (no new resource).

Reuses REASONING_ENGINE_ID from .env. Pushes the latest local agent code
without creating a fresh ReasoningEngine.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# MessageToDict shim — same as deploy.py.
from google.protobuf import json_format as _jf

_orig_to_dict = _jf.MessageToDict
_orig_to_json = _jf.MessageToJson


def _patched_to_dict(message, *args, **kwargs):
    if hasattr(message, "model_dump"):
        return message.model_dump(mode="json", by_alias=True, exclude_none=True)
    return _orig_to_dict(message, *args, **kwargs)


def _patched_to_json(message, *args, **kwargs):
    if hasattr(message, "model_dump_json"):
        return message.model_dump_json(by_alias=True, exclude_none=True)
    return _orig_to_json(message, *args, **kwargs)


_jf.MessageToDict = _patched_to_dict
_jf.MessageToJson = _patched_to_json

import vertexai  # noqa: E402
from a2a.types import AgentSkill, TransportProtocol  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from google.genai import types as genai_types  # noqa: E402
from vertexai.preview.reasoning_engines import A2aAgent  # noqa: E402
from vertexai.preview.reasoning_engines.templates.a2a import (  # noqa: E402
    create_agent_card,
)

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")


def main() -> None:
    project = os.environ["PROJECT_ID"]
    location = os.environ["LOCATION"]
    bucket = os.environ["STORAGE_BUCKET"]
    engine_id = os.environ["REASONING_ENGINE_ID"]
    api_endpoint = f"{location}-aiplatform.googleapis.com"

    resource_name = (
        f"projects/{project}/locations/{location}/reasoningEngines/{engine_id}"
    )
    print(f"≈ Updating {resource_name}")

    vertexai.init(
        project=project, location=location, api_endpoint=api_endpoint,
        staging_bucket=bucket,
    )
    client = vertexai.Client(
        project=project, location=location,
        http_options=genai_types.HttpOptions(api_version="v1beta1"),
    )

    skills = [
        AgentSkill(
            id="google_search",
            name="Google Search grounded answer",
            description=(
                "Answer questions using Google Search grounding. The "
                "agent runs as the Agent Runtime service account; access "
                "is gated upstream by GE's OAuth Authorization (Google IdP)."
            ),
            tags=["search", "grounding", "google"],
            examples=[
                "What was Vertex AI's last major release?",
                "Summarise the Cloud Run cold-start docs.",
            ],
        ),
        AgentSkill(
            id="whoami",
            name="Caller identity probe",
            description=(
                "Echo the Google identity claims that reached the agent "
                "container, after the GE -> Vertex AI -> Cloud Run proxy chain."
            ),
            tags=["diagnostic", "identity"],
            examples=["whoami", "who is calling me?"],
        ),
    ]
    card = create_agent_card(
        agent_name="ge_a2a_auth_agent",
        description=(
            "ADK agent on Agent Runtime, reached via GE Custom-A2A. Uses "
            "Google Search grounding (SA identity) and exposes a whoami "
            "diagnostic."
        ),
        skills=skills,
        streaming=True,
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )
    card.preferred_transport = TransportProtocol.http_json

    a2a_agent = A2aAgent(
        agent_card=card,
        agent_executor_builder=_build_executor,
    )
    a2a_agent.set_up()

    requirements = [
        r.strip()
        for r in (HERE / "agent" / "requirements.txt").read_text().splitlines()
        if r.strip() and not r.startswith("#")
    ]

    config = {
        "agent_framework": "google-adk",
        "staging_bucket": bucket,
        "gcs_dir_name": "ge_a2a_auth",
        "requirements": requirements,
        "extra_packages": ["agent"],
        "env_vars": {"NUM_WORKERS": "1"},
    }

    print("≈ Submitting agent_engines.update() — ~2-3 min")
    client.agent_engines.update(name=resource_name, agent=a2a_agent, config=config)
    print(f"✓ Updated: {resource_name}")


def _build_executor():
    from agent.agent_executor import build_executor
    return build_executor()


if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        print(f"Missing env var: {e}.", file=sys.stderr)
        sys.exit(1)
