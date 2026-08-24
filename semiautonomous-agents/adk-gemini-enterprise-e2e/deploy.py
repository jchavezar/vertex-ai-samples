"""Deploy ADK Executive Intelligence Agent to Vertex AI Agent Engine with Cloud Trace & Cloud Logging.

Usage:
    cd semiautonomous-agents/adk-gemini-enterprise-e2e
    uv run python deploy.py            # create new (or update if AGENT_ENGINE_RESOURCE is set)
    uv run python deploy.py new        # force fresh deployment
    uv run python deploy.py update     # update existing deployment
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from rich.console import Console
from rich.panel import Panel

console = Console()

PROJECT = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
if PROJECT == "jesusarguelles-sandbox":
    PROJECT = "vtxdemos"

DEPLOY_LOCATION = os.environ.get("LOCATION", "us-central1")
STAGING_BUCKET = os.environ.get("STAGING_BUCKET", "gs://vtxdemos-staging")
DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Executive Intelligence Analyst")

RUNTIME_ENV = {
    "GOOGLE_GENAI_USE_VERTEXAI": "true",
    "GOOGLE_CLOUD_LOCATION": os.environ.get("GOOGLE_CLOUD_LOCATION", "global"),
    "AGENT_MODEL": os.environ.get("AGENT_MODEL", "gemini-2.5-flash"),
}

REQUIREMENTS = [
    "google-cloud-aiplatform[adk,agent_engines]>=1.88.0",
    "google-adk>=0.1.0",
    "google-genai>=1.0.0",
    "pydantic>=2.0.0",
    "cloudpickle>=3.0.0",
]


def _build_app():
    from agent import root_agent  # local import after vertexai.init()
    return reasoning_engines.AdkApp(
        agent=root_agent,
        app_name="executive_intelligence_agent",
        enable_tracing=True
    )


def deploy_new():
    console.print(Panel.fit(
        f"[bold blue]Deploying ADK Agent to Vertex AI Agent Engine[/bold blue]\n"
        f"[cyan]Project:[/cyan] {PROJECT} | [cyan]Region:[/cyan] {DEPLOY_LOCATION}\n"
        f"[cyan]Staging Bucket:[/cyan] {STAGING_BUCKET}\n"
        f"[cyan]Tracing & Logging:[/cyan] [bold green]ENABLED[/bold green]"
    ))

    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION, staging_bucket=STAGING_BUCKET)
    app = _build_app()

    console.print("[yellow]Creating remote Agent Engine runtime deployment (this may take ~2-3 mins)...[/yellow]")
    remote = agent_engines.create(
        agent_engine=app,
        display_name=DISPLAY_NAME,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
        env_vars=RUNTIME_ENV,
    )

    console.print("\n" + "="*60)
    console.print(f"[bold green]✓ Deployment Complete![/bold green]")
    console.print(f"[bold]Resource Name:[/bold] {remote.resource_name}")
    console.print("="*60)

    # Save to local .env
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        content = env_file.read_text()
        if "AGENT_ENGINE_RESOURCE=" in content:
            import re
            content = re.sub(r'AGENT_ENGINE_RESOURCE=".*"', f'AGENT_ENGINE_RESOURCE="{remote.resource_name}"', content)
        else:
            content += f'\nAGENT_ENGINE_RESOURCE="{remote.resource_name}"\n'
        env_file.write_text(content)
        console.print(f"[cyan]Updated .env with AGENT_ENGINE_RESOURCE.[/cyan]")

    return remote


def deploy_update(resource_name: str):
    console.print(Panel.fit(f"[bold blue]Updating Deployment:[/bold blue] {resource_name}"))
    vertexai.init(project=PROJECT, location=DEPLOY_LOCATION, staging_bucket=STAGING_BUCKET)
    app = _build_app()

    remote = agent_engines.update(
        resource_name=resource_name,
        agent_engine=app,
        requirements=REQUIREMENTS,
        extra_packages=["agent"],
        env_vars=RUNTIME_ENV,
    )
    console.print(f"[bold green]✓ Successfully updated:[/bold green] {remote.resource_name}")
    return remote


def main():
    existing = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""

    if arg == "new":
        deploy_new()
    elif arg == "update":
        target = sys.argv[2] if len(sys.argv) > 2 else existing
        if not target:
            console.print("[red]Error: AGENT_ENGINE_RESOURCE not found in .env and not passed as arg.[/red]")
            sys.exit(1)
        deploy_update(target)
    else:
        if existing:
            console.print(f"[cyan]Found existing resource in .env: {existing}[/cyan]")
            deploy_update(existing)
        else:
            deploy_new()


if __name__ == "__main__":
    main()
