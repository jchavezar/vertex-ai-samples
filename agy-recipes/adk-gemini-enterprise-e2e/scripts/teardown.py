# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "rich>=13.0.0",
# ]
# ///
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def teardown_recipe():
    console.print(Panel.fit("[bold blue]Tearing Down ADK Gemini Enterprise E2E Recipe[/bold blue]"))

    script_dir = os.path.dirname(os.path.abspath(__file__))
    recipe_root = os.path.dirname(script_dir)
    tracker_path = os.path.join(recipe_root, "last_setup_resources.json")

    if os.path.exists(tracker_path):
        os.remove(tracker_path)
        console.print(f"  [green]✓[/green] Removed tracker file: {tracker_path}")
    else:
        console.print("  [yellow]![/yellow] Tracker file does not exist.")

    console.print(Panel.fit("[bold green]Teardown Complete. Local state cleanly removed.[/bold green]"))

if __name__ == "__main__":
    teardown_recipe()
