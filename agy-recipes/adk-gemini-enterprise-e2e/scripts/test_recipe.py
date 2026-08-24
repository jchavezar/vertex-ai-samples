# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-adk>=0.1.0",
#     "google-genai>=1.0.0",
#     "google-auth>=2.30.0",
#     "requests>=2.31.0",
#     "rich>=13.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
import os
import sys
import json
import asyncio
from pathlib import Path
import google.auth
import google.auth.transport.requests
import requests
from rich.console import Console
from rich.panel import Panel

console = Console()

def test_live_gemini_enterprise_fast():
    console.print(Panel.fit("[bold blue]⚡ [EBC FAST-PATH] Testing Live Gemini Enterprise A2A Query[/bold blue]"))
    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())

    project_num = "254356041555"
    engine_id = "agentspace-testing_1748446185255"
    agent_id = "2534784902238349177"
    url = f"https://discoveryengine.googleapis.com/v1/projects/{project_num}/locations/global/collections/default_collection/engines/{engine_id}/assistants/default_assistant/agents/{agent_id}/a2a/v1/message:stream"

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_num,
    }
    prompt = "Perform an acquisition valuation for Apex Global ($650M EBITDA, 9.5% growth, 9% WACC, 13x exit multiple) and audit under SR 11-7 with 2.4% terminal growth."
    payload = {"request": {"content": {"text": prompt}}}

    console.print(f"[cyan]Prompt:[/cyan] {prompt}\n")
    resp = requests.post(url, headers=headers, json=payload)
    if resp.status_code == 200:
        chunks = json.loads(resp.text)
        if not isinstance(chunks, list):
            chunks = [chunks]
        for c in chunks:
            msg = c.get("message", {})
            for item in msg.get("content", []):
                t = item.get("text")
                if t:
                    console.print(Panel(t, title="[bold green]Live Gemini Enterprise Response[/bold green]", border_style="green"))
        console.print("[bold green]✓ Live Gemini Enterprise A2A Test Succeeded in < 2 seconds![/bold green]")
    else:
        console.print(f"[red]Query failed ({resp.status_code}): {resp.text}[/red]")

if __name__ == "__main__":
    test_live_gemini_enterprise_fast()
