# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai>=1.0.0",
#     "google-auth>=2.0.0",
#     "rich>=13.0.0",
# ]
# ///
import os
import time
from rich.console import Console
from rich.panel import Panel
from google import genai

console = Console()

def test_recipe():
    console.print(Panel.fit("[bold blue]Testing Vertex AI Managed Agent Remote Sandbox Interaction[/bold blue]"))

    project_id = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
    if project_id == "jesusarguelles-sandbox":
        project_id = "vtxdemos"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

    client = genai.Client(vertexai=True, project=project_id, location=location)

    console.print(f"[cyan][1/2][/cyan] Dispatching verification prompt to remote Linux container...")
    start_time = time.time()
    interaction = client.interactions.create(
        agent="antigravity-preview-05-2026",
        input="Execute a fast Python calculation in your /workspace container to compute sum(range(1001)). Output the exact sum.",
        system_instruction="You are an autonomous data scientist. Always execute Python code in /workspace to verify computational results.",
        environment={"type": "remote"},
        background=True
    )

    console.print(f"  [green]✓[/green] Interaction submitted: [bold]{interaction.id}[/bold]")
    console.print(f"[cyan][2/2][/cyan] Awaiting execution in remote container...")

    while True:
        inter = client.interactions.get(id=interaction.id)
        if inter.status in ("completed", "failed", "cancelled"):
            if inter.status != "completed":
                raise RuntimeError(f"Interaction ended with status: {inter.status}")
            elapsed = time.time() - start_time
            console.print(f"  [green]✓[/green] Completed in {elapsed:.2f}s | Sandbox ID: {getattr(inter, 'environment_id', 'N/A')}")
            console.print(Panel(inter.output_text, title="Agent Verified Output", border_style="green"))
            break
        time.sleep(2)

if __name__ == "__main__":
    test_recipe()
