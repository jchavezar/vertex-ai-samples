"""Local sanity check for the ADK Agent — tests offline tool calling and response generation."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

# Explicitly override project and location to vtxdemos
project_id = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
if project_id == "jesusarguelles-sandbox":
    project_id = "vtxdemos"

os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_LOCATION"] = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

from google.adk.runners import InMemoryRunner
from google.genai import types
from rich.console import Console
from rich.panel import Panel
from agent import root_agent

console = Console()

async def main(prompt: str = "Perform a DCF valuation for Acme Corp with initial EBITDA $500M, 8% growth, WACC 8.5%, and 14.5x exit multiple. Then audit model risk under SR 11-7."):
    console.print(Panel.fit(f"[bold blue]Testing ADK Agent Locally (InMemoryRunner)[/bold blue]\n[cyan]Prompt:[/cyan] {prompt}"))

    runner = InMemoryRunner(agent=root_agent, app_name="executive_local")
    session = await runner.session_service.create_session(
        app_name="executive_local", user_id="local_tester"
    )

    user_msg = types.Content(
        role="user",
        parts=[types.Part.from_text(text=prompt)],
    )

    console.print("\n[bold green]Streaming Agent Execution Steps:[/bold green]")
    async for event in runner.run_async(
        user_id="local_tester", session_id=session.id, new_message=user_msg
    ):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    console.print(p.text, end="")
                elif getattr(p, "function_call", None):
                    fc = p.function_call
                    console.print(f"\n[bold yellow]⚡ [TOOL CALL][/bold yellow] [bold]{fc.name}[/bold]({fc.args})")
                elif getattr(p, "function_response", None):
                    fr = p.function_response
                    console.print(f"[bold magenta]↩ [TOOL RESPONSE][/bold magenta] {fr.response}\n")

    console.print("\n\n" + "="*50)
    console.print("[bold green]✓ Local Smoke Test Completed Successfully![/bold green]")
    console.print("="*50)

if __name__ == "__main__":
    test_prompt = sys.argv[1] if len(sys.argv) > 1 else "Perform a DCF valuation for Acme Corp with initial EBITDA $500M, 8% growth, WACC 8.5%, and 14.5x exit multiple. Then audit model risk under SR 11-7."
    asyncio.run(main(test_prompt))
