"""Test query directly through Gemini Enterprise using Discovery Engine A2A Protocol.

🤖 ANTIGRAVITY AGENT HITL MANDATE:
Before proceeding with Gemini Enterprise testing, verify GE_PROJECT_NUMBER and AS_APP.
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

PROJECT_NUMBER = os.environ.get("GE_PROJECT_NUMBER", "254356041555").strip()
ENGINE_ID = os.environ.get("AS_APP", "agentspace-testing_1748446185255").strip()
# Discovered registered agent ID or override via env
AGENT_ID = os.environ.get("GE_AGENT_ID", "2534784902238349177").strip()


def query_gemini_enterprise_agent(prompt: str):
    console.print(Panel.fit(
        f"[bold blue]Testing Direct Gemini Enterprise A2A Invocation[/bold blue]\n"
        f"[cyan]Project Number:[/cyan] {PROJECT_NUMBER}\n"
        f"[cyan]Engine ID:[/cyan] {ENGINE_ID}\n"
        f"[cyan]Registered Agent ID:[/cyan] {AGENT_ID}\n"
        f"[cyan]Prompt:[/cyan] {prompt}"
    ))

    creds, _ = google.auth.default()
    creds.refresh(google.auth.transport.requests.Request())

    url = (
        f"https://discoveryengine.googleapis.com/v1/"
        f"projects/{PROJECT_NUMBER}/locations/global/"
        f"collections/default_collection/engines/{ENGINE_ID}/"
        f"assistants/default_assistant/agents/{AGENT_ID}/"
        f"a2a/v1/message:stream"
    )

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": PROJECT_NUMBER,
    }

    payload = {
        "request": {
            "content": {
                "text": prompt
            }
        }
    }

    console.print("[cyan]Sending request to Gemini Enterprise A2A stream endpoint...[/cyan]\n")
    resp = requests.post(url, headers=headers, json=payload)

    if resp.status_code != 200:
        console.print(f"[bold red]Query failed ({resp.status_code}):[/bold red] {resp.text}")
        return

    try:
        chunks = json.loads(resp.text)
        if not isinstance(chunks, list):
            chunks = [chunks]

        for chunk in chunks:
            msg = chunk.get("message", {})
            metadata = msg.get("metadata", {})
            answer = metadata.get("answer", {})
            author = answer.get("adkAuthor", "N/A")
            context_id = msg.get("contextId", "")

            console.print(f"[bold cyan]Gemini Enterprise Session ID:[/bold cyan] {context_id.split('/')[-1] if context_id else 'N/A'}")
            console.print(f"[bold cyan]ADK Author Resolution:[/bold cyan] [bold green]{author}[/bold green]\n")

            content_list = msg.get("content", [])
            for c in content_list:
                text = c.get("text", "")
                if text:
                    console.print(Panel(text, title="[bold green]Gemini Enterprise Response[/bold green]", border_style="green"))

            # Inspect replies
            for reply in answer.get("replies", []):
                grounded = reply.get("groundedContent", {}).get("content", {})
                r_text = grounded.get("text", "")
                if r_text and r_text != content_list[0].get("text", ""):
                    console.print(f"[green]{r_text}[/green]")

        console.print("\n" + "="*60)
        console.print("[bold green]✓ Gemini Enterprise Direct Verification Succeeded![/bold green]")
        console.print("="*60)

    except Exception as e:
        console.print(f"[bold red]Error parsing response:[/bold red] {e}\nRaw: {resp.text}")


if __name__ == "__main__":
    test_prompt = sys.argv[1] if len(sys.argv) > 1 else "Perform a DCF valuation for Acme Corp with initial EBITDA 500 million, 8% growth, WACC 8.5%, and 14.5x exit multiple. Then audit model risk under SR 11-7 assuming terminal growth 3%."
    query_gemini_enterprise_agent(test_prompt)
