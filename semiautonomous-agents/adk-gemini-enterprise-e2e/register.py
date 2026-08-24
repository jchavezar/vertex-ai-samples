"""Register the deployed ADK Agent in Gemini Enterprise and share with ALL_USERS.

Usage:
    cd semiautonomous-agents/adk-gemini-enterprise-e2e
    uv run python register.py            # register + share with ALL_USERS
    uv run python register.py agent      # register only (no sharing change)
    uv run python register.py share <agent-resource-name>   # share existing
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

import google.auth
import google.auth.transport.requests
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

GE_PROJECT_ID = os.environ.get("GE_PROJECT_ID", "vtxdemos")
GE_PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555")
AS_APP = os.environ.get("AS_APP", "agentspace-testing_1748446185255")
AGENT_ENGINE_RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "")

AGENT_DISPLAY_NAME = os.environ.get("AGENT_DISPLAY_NAME", "Executive Financial & Risk Intelligence Analyst")
AGENT_DESCRIPTION = os.environ.get(
    "AGENT_DESCRIPTION",
    "Autonomous ADK quantitative agent for DCF enterprise valuation, M&A risk sensitivity, and OCC/FRB SR 11-7 model governance.",
)
TOOL_DESCRIPTION = os.environ.get(
    "TOOL_DESCRIPTION",
    "Use this agent for evaluating company acquisitions, calculating discounted cash flows (DCF), running sensitivity shocks, and auditing model risk under SR 11-7 regulatory standards.",
)
AGENT_ICON = os.environ.get(
    "AGENT_ICON",
    "https://fonts.gstatic.com/s/i/short-term/release/googlesymbols/finance_chip/default/24px.svg",
)


def _headers() -> dict:
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": GE_PROJECT_ID,
    }


def _base() -> str:
    return f"https://discoveryengine.googleapis.com/v1alpha/projects/{GE_PROJECT_NUMBER}/locations/global"


def register_agent() -> str | None:
    if not AGENT_ENGINE_RESOURCE:
        console.print("[bold red]Error: AGENT_ENGINE_RESOURCE is empty. Run deploy.py first or set it in .env.[/bold red]")
        sys.exit(1)

    url = (
        f"{_base()}/collections/default_collection/engines/{AS_APP}"
        "/assistants/default_assistant/agents"
    )
    payload = {
        "displayName": AGENT_DISPLAY_NAME,
        "description": AGENT_DESCRIPTION,
        "icon": {"uri": AGENT_ICON},
        "adk_agent_definition": {
            "tool_settings": {"tool_description": TOOL_DESCRIPTION},
            "provisioned_reasoning_engine": {
                "reasoning_engine": AGENT_ENGINE_RESOURCE,
            },
        },
    }

    console.print(Panel.fit(
        f"[bold blue]Registering ADK Agent in Gemini Enterprise[/bold blue]\n"
        f"[cyan]App ID:[/cyan] {AS_APP}\n"
        f"[cyan]Display Name:[/cyan] {AGENT_DISPLAY_NAME}\n"
        f"[cyan]Bound Reasoning Engine:[/cyan] {AGENT_ENGINE_RESOURCE}"
    ))

    resp = requests.post(url, headers=_headers(), json=payload)
    if resp.status_code in (200, 201):
        name = resp.json().get("name", "")
        console.print(f"[bold green]✓ Agent Registered Successfully![/bold green]\n[bold]GE Agent Resource:[/bold] {name}")
        return name

    console.print(f"[bold red]Registration Failed ({resp.status_code}):[/bold red] {resp.text}")
    return None


def share_agent(agent_name: str) -> bool:
    url = f"https://discoveryengine.googleapis.com/v1alpha/{agent_name}?updateMask=sharingConfig"
    console.print(f"[cyan]Sharing agent with ALL_USERS...[/cyan]")
    resp = requests.patch(
        url,
        headers=_headers(),
        json={"sharingConfig": {"scope": "ALL_USERS"}},
    )
    if resp.status_code == 200:
        console.print("[bold green]✓ Shared with ALL_USERS in Gemini Enterprise![/bold green]")
        return True
    console.print(f"[yellow]Warning ({resp.status_code}):[/yellow] {resp.text}")
    return False


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"

    if mode == "share":
        target = sys.argv[2] if len(sys.argv) > 2 else ""
        if not target:
            console.print("[red]Usage: register.py share <agent-resource-name>[/red]")
            sys.exit(1)
        share_agent(target)
    elif mode == "agent":
        register_agent()
    else:
        name = register_agent()
        if name:
            share_agent(name)


if __name__ == "__main__":
    main()
