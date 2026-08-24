"""Test query against a deployed Vertex AI Agent Engine / Reasoning Engine."""
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

PROJECT = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
LOCATION = os.environ.get("LOCATION", "us-central1")
RESOURCE = os.environ.get("AGENT_ENGINE_RESOURCE", "")


def test_remote_stream_query(prompt: str):
    if not RESOURCE:
        console.print("[bold red]Error: AGENT_ENGINE_RESOURCE is not set in .env[/bold red]")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold blue]Testing Remote Vertex AI Agent Engine Query[/bold blue]\n"
        f"[cyan]Resource:[/cyan] {RESOURCE}\n"
        f"[cyan]Prompt:[/cyan] {prompt}"
    ))

    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())

    # Direct REST streamQuery SSE endpoint
    url = f"https://{LOCATION}-aiplatform.googleapis.com/v1/{RESOURCE}:streamQuery?alt=sse"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "x-goog-user-project": PROJECT,
    }
    payload = {
        "class_method": "async_stream_query",
        "input": {
            "message": prompt
        }
    }

    console.print("[cyan]Connecting to live Agent Engine stream...[/cyan]\n")
    response = requests.post(url, headers=headers, json=payload, stream=True)
    if response.status_code != 200:
        console.print(f"[bold red]Query failed ({response.status_code}):[/bold red] {response.text}")
        return

    for line in response.iter_lines():
        if line:
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                raw_data = decoded[6:]
                try:
                    data = json.loads(raw_data)
                    console.print(data)
                except Exception:
                    console.print(raw_data)

    console.print("\n[bold green]✓ Remote Stream Query Finished![/bold green]")


if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Calculate enterprise valuation for $450M EBITDA with 9% growth and 9% WACC, then perform an SR 11-7 model audit."
    test_remote_stream_query(prompt)
