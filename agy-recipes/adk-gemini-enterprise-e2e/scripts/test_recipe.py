# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-adk>=0.1.0",
#     "google-genai>=1.0.0",
#     "rich>=13.0.0",
#     "python-dotenv>=1.0.0",
# ]
# ///
import os
import sys
import asyncio
from pathlib import Path

# Locate agent package
workspace_root = Path(__file__).resolve().parent.parent.parent.parent
agent_dir = workspace_root / "semiautonomous-agents" / "adk-gemini-enterprise-e2e"
sys.path.insert(0, str(agent_dir))

os.environ["GOOGLE_CLOUD_PROJECT"] = "vtxdemos"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from google.adk.runners import InMemoryRunner
from google.genai import types
from rich.console import Console
from rich.panel import Panel
from agent import root_agent

console = Console()

async def run_smoke():
    console.print(Panel.fit("[bold blue]Testing ADK Recipe Smoke Execution[/bold blue]"))
    runner = InMemoryRunner(agent=root_agent, app_name="executive_recipe_test")
    session = await runner.session_service.create_session(app_name="executive_recipe_test", user_id="recipe_tester")

    prompt = "Calculate DCF enterprise value for $300M EBITDA, 7% growth, 8.5% WACC, and 12x exit multiple."
    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])

    console.print(f"[cyan]Prompt:[/cyan] {prompt}\n")
    async for event in runner.run_async(user_id="recipe_tester", session_id=session.id, new_message=user_msg):
        if event.content and event.content.parts:
            for p in event.content.parts:
                if getattr(p, "text", None):
                    console.print(p.text, end="")
                elif getattr(p, "function_call", None):
                    console.print(f"\n[bold yellow]⚡ Calling {p.function_call.name}...[/bold yellow]")

    console.print("\n\n[bold green]✓ Recipe Smoke Test Passed![/bold green]")

if __name__ == "__main__":
    asyncio.run(run_smoke())
