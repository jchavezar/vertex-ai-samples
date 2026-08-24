# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-genai>=1.0.0",
#     "google-auth>=2.0.0",
#     "rich>=13.0.0",
# ]
# ///
import os
import json
import time
from rich.console import Console
from rich.panel import Panel
from google import genai
import google.auth

console = Console()

def setup_managed_agent_recipe():
    console.print(Panel.fit("[bold blue]Vertex AI Managed Agents Setup & Verification[/bold blue]"))

    # 1. Resolve GCP Project & Credentials
    project_id = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
    if project_id == "jesusarguelles-sandbox":
        project_id = "vtxdemos"
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "global")

    console.print(f"[cyan][1/3][/cyan] Authenticating via Application Default Credentials (ADC)...")
    credentials, detected_project = google.auth.default()
    console.print(f"  [green]✓[/green] Credentials detected. Project: [bold]{project_id}[/bold] | Location: [bold]{location}[/bold]")

    # 2. Verify Client Connection to Vertex AI Managed Agents
    console.print(f"[cyan][2/3][/cyan] Initializing Vertex AI Managed Agent client...")
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location,
    )
    console.print(f"  [green]✓[/green] Client initialized successfully.")

    # 3. Write Resource Tracker
    resource_tracker = {
        "recipe": "managed-agent-sandbox-chat",
        "project_id": project_id,
        "location": location,
        "agent_model": "antigravity-preview-05-2026",
        "status": "ready",
        "timestamp": time.time(),
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    recipe_root = os.path.dirname(script_dir)
    tracker_path = os.path.join(recipe_root, "last_setup_resources.json")

    with open(tracker_path, "w") as f:
        json.dump(resource_tracker, f, indent=2)

    console.print(f"[cyan][3/3][/cyan] Saved configuration to tracker file: {tracker_path}")
    console.print(Panel.fit("[bold green]Setup Complete! Launch UI with ./antigravity-sandbox-chat/start.sh[/bold green]"))

if __name__ == "__main__":
    setup_managed_agent_recipe()
