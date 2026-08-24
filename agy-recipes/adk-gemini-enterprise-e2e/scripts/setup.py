# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "google-cloud-aiplatform[adk,agent_engines]>=1.88.0",
#     "google-genai>=1.0.0",
#     "google-auth>=2.30.0",
#     "rich>=13.0.0",
# ]
# ///
import os
import json
import time
from rich.console import Console
from rich.panel import Panel
import google.auth
import vertexai

console = Console()

def setup_recipe():
    console.print(Panel.fit("[bold blue]Setting Up ADK Gemini Enterprise E2E Recipe[/bold blue]"))

    project_id = os.environ.get("VERTEX_PROJECT_ID", os.environ.get("GOOGLE_CLOUD_PROJECT", "vtxdemos"))
    if project_id == "jesusarguelles-sandbox":
        project_id = "vtxdemos"
    location = os.environ.get("LOCATION", "us-central1")
    staging_bucket = os.environ.get("STAGING_BUCKET", "gs://vtxdemos-staging")

    console.print("[cyan][1/3][/cyan] Checking Application Default Credentials...")
    creds, detected = google.auth.default()
    console.print(f"  [green]✓[/green] ADC active for project: [bold]{project_id}[/bold]")

    console.print("[cyan][2/3][/cyan] Initializing Vertex AI SDK...")
    vertexai.init(project=project_id, location=location, staging_bucket=staging_bucket)
    console.print(f"  [green]✓[/green] Vertex AI initialized in [bold]{location}[/bold]")

    tracker = {
        "recipe": "adk-gemini-enterprise-e2e",
        "project_id": project_id,
        "location": location,
        "staging_bucket": staging_bucket,
        "agent_app": "executive_intelligence_agent",
        "status": "ready",
        "timestamp": time.time(),
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    recipe_root = os.path.dirname(script_dir)
    tracker_path = os.path.join(recipe_root, "last_setup_resources.json")

    with open(tracker_path, "w") as f:
        json.dump(tracker, f, indent=2)

    console.print(f"[cyan][3/3][/cyan] Saved configuration to tracker file: {tracker_path}")
    console.print(Panel.fit("[bold green]Setup Complete! Ready for deployment and testing.[/bold green]"))

if __name__ == "__main__":
    setup_recipe()
