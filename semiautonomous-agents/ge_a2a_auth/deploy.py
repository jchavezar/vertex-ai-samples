"""Deploy the ADK agent to Vertex AI Agent Runtime as a native A2A endpoint.

After deploy the agent is reachable at:

    https://{LOCATION}-aiplatform.googleapis.com/v1beta1/
    projects/{P}/locations/{L}/reasoningEngines/{ID}/a2a

Auth is Google Bearer (user or SA access token with cloud-platform scope).

Writes the resolved A2A URL + reasoningEngine ID back into .env so the
follow-up scripts (create_authorization.py, register_ge_agent.py) can pick
them up without manual copy/paste.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Apply the json_format.MessageToDict shim BEFORE importing vertexai — the
# deploy path calls MessageToDict on the pydantic AgentCard from a2a-sdk 0.x,
# which has no .DESCRIPTOR. Fall back to .model_dump() in that case.
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

import httpx  # noqa: E402
import vertexai  # noqa: E402
from a2a.types import AgentSkill, TransportProtocol  # noqa: E402
from dotenv import load_dotenv  # noqa: E402
from google.auth import default  # noqa: E402
from google.auth.transport.requests import Request  # noqa: E402
from google.genai import types as genai_types  # noqa: E402
from vertexai.preview.reasoning_engines import A2aAgent  # noqa: E402
from vertexai.preview.reasoning_engines.templates.a2a import (  # noqa: E402
    create_agent_card,
)

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")


def bearer_token() -> str:
    creds, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def update_env(updates: dict[str, str]) -> None:
    env_path = HERE / ".env"
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text().splitlines()
    seen = set()
    out: list[str] = []
    for line in lines:
        key = line.split("=", 1)[0] if "=" in line else ""
        if key in updates:
            out.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            out.append(line)
    for k, v in updates.items():
        if k not in seen:
            out.append(f"{k}={v}")
    env_path.write_text("\n".join(out) + "\n")


def main() -> None:
    project = os.environ["PROJECT_ID"]
    location = os.environ["LOCATION"]
    bucket = os.environ["STORAGE_BUCKET"]
    api_endpoint = f"{location}-aiplatform.googleapis.com"

    print(f"≈ Deploying to {project}/{location} (bucket={bucket})")

    vertexai.init(
        project=project,
        location=location,
        api_endpoint=api_endpoint,
        staging_bucket=bucket,
    )

    client = vertexai.Client(
        project=project,
        location=location,
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

    agent_card = create_agent_card(
        agent_name="ge_a2a_auth_agent",
        description=(
            "Diagnostic ADK agent deployed to Agent Runtime, registered in "
            "Gemini Enterprise via the Custom-A2A path, authenticated through "
            "an OAuth2 Authorization resource (cloud-platform scope)."
        ),
        skills=skills,
        streaming=True,
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
    )
    # create_agent_card defaults preferred_transport to JSONRPC; the A2aAgent
    # validator rejects anything that isn't http_json. Force it.
    agent_card.preferred_transport = TransportProtocol.http_json

    a2a_agent = A2aAgent(
        agent_card=agent_card,
        agent_executor_builder=_build_executor,
    )
    # Local sanity init (doesn't deploy; just wires it up).
    a2a_agent.set_up()
    print("✓ Local A2aAgent wired")

    requirements_path = HERE / "agent" / "requirements.txt"
    requirements = [
        r.strip()
        for r in requirements_path.read_text().splitlines()
        if r.strip() and not r.startswith("#")
    ]

    config = {
        "display_name": "ge_a2a_auth diagnostic",
        "description": (
            "ADK agent on Agent Runtime exposing A2A, registered in GE via "
            "Custom-A2A with OAuth2-cloud-platform bridge auth."
        ),
        "agent_framework": "google-adk",
        "staging_bucket": bucket,
        "gcs_dir_name": "ge_a2a_auth",
        "requirements": requirements,
        "http_options": {"api_version": "v1beta1"},
        "max_instances": 1,
        "extra_packages": ["agent"],
        "env_vars": {"NUM_WORKERS": "1"},
    }

    print("≈ Submitting agent_engines.create() — this takes ~5 min the first time")
    remote = client.agent_engines.create(agent=a2a_agent, config=config)
    resource = remote.api_resource.name
    engine_id = resource.split("/")[-1]
    a2a_url = f"https://{api_endpoint}/v1beta1/{resource}/a2a"
    print(f"✓ Deployed: {resource}")
    print(f"  A2A URL: {a2a_url}")

    card_endpoint = f"{a2a_url}/v1/card"
    headers = {"Authorization": f"Bearer {bearer_token()}"}
    resp = httpx.get(card_endpoint, headers=headers, timeout=30)
    resp.raise_for_status()
    fetched_card = resp.json()
    print("✓ /v1/card fetched OK")

    # Pin streaming=true and overwrite url with the *public* A2A url so GE
    # routes to the right place.
    fetched_card["url"] = a2a_url
    fetched_card.setdefault("capabilities", {})["streaming"] = True

    card_path = HERE / "agent_card.json"
    card_path.write_text(json.dumps(fetched_card, indent=2))
    print(f"✓ Saved {card_path}")

    update_env({"REASONING_ENGINE_ID": engine_id, "A2A_URL": a2a_url})
    print("✓ .env updated (REASONING_ENGINE_ID, A2A_URL)")


def _build_executor():
    # Imported inside the function so it's picklable into the AE bundle.
    from agent.agent_executor import build_executor

    return build_executor()


if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        print(f"Missing env var: {e}. Copy .env.sample to .env first.", file=sys.stderr)
        sys.exit(1)
