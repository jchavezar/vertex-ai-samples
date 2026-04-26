"""Deploy the report-generator to Vertex AI Agent Engine.

NOTE: WeasyPrint requires native libs (libpango, cairo, harfbuzz). Agent
Engine builds use a Debian base; we declare the apt deps in
`extra_packages` style via a Dockerfile-free approach is NOT supported
today, so for production you should containerise via the `agent-starter-pack`
Cloud Run path. This script targets the *managed Agent Engine* path —
for runs that include PDF rendering, prefer `run_local.py` or the
Cloud Run deploy.
"""
from __future__ import annotations

import os

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

load_dotenv()

PROJECT = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
STAGING = os.environ["STAGING_BUCKET"]

vertexai.init(project=PROJECT, location=LOCATION, staging_bucket=STAGING)

from agent import root_agent  # noqa: E402

app = AdkApp(agent=root_agent, enable_tracing=True)

remote = agent_engines.create(
    agent_engine=app,
    requirements="requirements.txt",
    extra_packages=["./agent"],
    display_name="report-generator",
    description="Multi-agent report generator with Google Search + PDF rendering",
    env_vars={
        "GOOGLE_GENAI_USE_VERTEXAI": "True",
        "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "True",
        "REPORT_PLANNER_MODEL": os.environ.get("REPORT_PLANNER_MODEL", "gemini-3-flash-preview"),
        "REPORT_RESEARCH_MODEL": os.environ.get("REPORT_RESEARCH_MODEL", "gemini-3-flash-preview"),
        "REPORT_WRITER_MODEL": os.environ.get("REPORT_WRITER_MODEL", "gemini-3-flash-preview"),
    },
)

print(f"Deployed: {remote.resource_name}")
