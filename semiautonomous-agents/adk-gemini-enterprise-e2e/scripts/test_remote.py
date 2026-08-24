"""Test query against a deployed Vertex AI Agent Engine / Reasoning Engine.

🤖 ANTIGRAVITY AGENT HITL MANDATE:
Before proceeding with remote testing, verify PROJECT_ID, REGION, and AGENT_ENGINE_RESOURCE.
If not set in .env, prompt the human:
"Ask the human for PROJECT_ID, REGION, STAGING_BUCKET, and GE_PROJECT_NUMBER before proceeding if they are not in .env. Do NOT proceed until confirmed."

REQUIRED DEPENDENCIES:
  uv add google-cloud-aiplatform[adk,agent_engines] google-genai requests google-auth rich pydantic cloudpickle
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env", override=True)

import google.auth
import google.auth.transport.requests
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

PROJECT = os.environ.get("PROJECT_ID", os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))).strip()
LOCATION = os.environ.get("REGION", os.environ.get("LOCATION", "us-central1")).strip()
RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "").strip()


def test_remote_stream_query(prompt: str):
    if not RESOURCE:
        console.print("[bold red]Error: AGENT_ENGINE_RESOURCE is not set in .env[/bold red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold blue]Testing Live Vertex AI Agent Engine Query[/bold blue]\n"
        f"[cyan]Resource:[/cyan] {RESOURCE}\n"
        f"[cyan]Prompt:[/cyan] {prompt}"
    ))

    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT,
    }

    # Step 1: Create session
    console.print("[cyan][1/2] Creating agent session via async_create_session...[/cyan]")
    session_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{RESOURCE}:query"
    session_payload = {
        "class_method": "async_create_session",
        "input": {
            "user_id": "executive_tester"
        }
    }
    s_resp = requests.post(session_url, headers=headers, json=session_payload)
    if s_resp.status_code != 200:
        console.print(f"[bold red]Session creation failed ({s_resp.status_code}):[/bold red] {s_resp.text}")
        return

    session_data = s_resp.json()
    output_obj = session_data.get("output", {})
    session_id = output_obj.get("id") if isinstance(output_obj, dict) else output_obj
    console.print(f"  [green]✓[/green] Session created: [bold]{session_id}[/bold]")

    # Step 2: Stream query
    console.print("[cyan][2/2] Streaming query via async_stream_query...[/cyan]\n")
    stream_url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{RESOURCE}:streamQuery?alt=sse"
    query_payload = {
        "class_method": "async_stream_query",
        "input": {
            "user_id": "executive_tester",
            "session_id": session_id,
            "message": prompt
        }
    }

    response = requests.post(stream_url, headers=headers, json=query_payload, stream=True)
    if response.status_code != 200:
        console.print(f"[bold red]Stream Query failed ({response.status_code}):[/bold red] {response.text}")
        return

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                raw_data = decoded[6:]
                try:
                    event = json.loads(raw_data)
                    # Check for tool calls / parts
                    content = event.get("content", {})
                    parts = content.get("parts", [])
                    for p in parts:
                        if "text" in p:
                            console.print(p["text"], end="")
                        elif "functionCall" in p:
                            fc = p["functionCall"]
                            console.print(f"\n[bold yellow]⚡ [REMOTE TOOL CALL][/bold yellow] [bold]{fc.get('name')}[/bold]({fc.get('args')})")
                        elif "functionResponse" in p:
                            fr = p["functionResponse"]
                            console.print(f"[bold magenta]↩ [REMOTE TOOL RESPONSE][/bold magenta] {fr.get('response')}\n")
                except Exception:
                    console.print(raw_data)

    console.print("\n\n" + "="*60)
    console.print("[bold green]✓ Live Remote Stream Query Succeeded![/bold green]")
    console.print("="*60)


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Calculate enterprise valuation for $500M EBITDA with 8% growth, 8.5% WACC, and 14.5x exit multiple. Then perform an SR 11-7 model audit."
    test_remote_stream_query(prompt)
