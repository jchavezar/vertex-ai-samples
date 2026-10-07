#!/usr/bin/env python3
"""Google ADK Real-Time Intelligence Agent — Live IDE Execution & Demonstration.

This script demonstrates how to run and stream an ADK agent in real-time using:
  1. `google.adk.agents.Agent` (The intelligent orchestrator)
  2. `google.adk.runners.InMemoryRunner` (The stateful execution engine)
  3. `google.genai.types.Content` (Standard GenAI message payloads)
  4. Real-time streaming of model reasoning, tool invocations, and responses.

Run directly in your terminal:
    python main.py
"""

import asyncio
import os
import sys
import uuid
import warnings

# Suppress minor experimental schema warnings for clean presentation
warnings.filterwarnings("ignore", category=UserWarning)

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from google.adk.runners import InMemoryRunner
from google.genai import types
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

# Import the root agent from our modular package
from app.agent import root_agent, MODEL_NAME

console = Console()

PRESET_PROMPTS = [
    (
        "Multi-Tool Synergy (Stocks + Global Weather)",
        "What is Alphabet (GOOGL) trading at right now compared to Apple (AAPL), and what is the current weather in Tokyo?",
    ),
    (
        "Crypto & Equities Real-Time Pulse",
        "Give me the live price and 24h change for Bitcoin (BTC) and Ethereum (ETH), plus Nvidia (NVDA) stock.",
    ),
    (
        "Company Fundamentals & Valuation",
        "Provide a profile of Microsoft (MSFT), including its sector, business summary, and latest stock quote.",
    ),
    (
        "Global Weather Multi-City Comparison",
        "What are the current temperatures and weather conditions in London, New York, and San Francisco?",
    ),
]


def print_banner() -> None:
    """Prints a styled banner explaining the architecture for the presentation."""
    grid = Table.grid(padding=1)
    grid.add_column(style="bold cyan", justify="left")
    grid.add_column(style="white")

    grid.add_row("Agent:", f"[bold green]{root_agent.name}[/bold green]")
    grid.add_row("Foundation Model:", f"[bold yellow]{MODEL_NAME}[/bold yellow] (Vertex AI)")
    grid.add_row(
        "Registered Tools:",
        "[magenta]get_stock_quote[/magenta], [magenta]get_company_profile[/magenta], [magenta]get_live_weather[/magenta], [magenta]get_crypto_quote[/magenta]",
    )
    grid.add_row("Execution Engine:", "[bold blue]ADK InMemoryRunner (Async Event Stream)[/bold blue]")

    panel = Panel(
        grid,
        title="[bold white]🌟 Google Agent Development Kit (ADK) — Live Demo 🌟[/bold white]",
        border_style="cyan",
        subtitle="[dim]Real-time Tool Execution & Multi-Turn State[/dim]",
    )
    console.print(panel)


async def execute_turn(runner: InMemoryRunner, session_id: str, user_prompt: str) -> None:
    """Executes a single conversational turn with live real-time event streaming."""
    console.print(f"\n[bold yellow]User ➔[/bold yellow] {user_prompt}\n")

    # 1. Package the user's prompt as an ADK/GenAI Content message
    user_message = types.Content(
        role="user",
        parts=[types.Part.from_text(text=user_prompt)],
    )

    console.print("[dim]⚡ Streaming ADK event pipeline...[/dim]")

    # 2. Iterate asynchronously over the agent event stream
    accumulated_response: list[str] = []

    async for event in runner.run_async(
        user_id="presenter_user",
        session_id=session_id,
        new_message=user_message,
    ):
        # A. Detect Tool Invocations (Gemini decided to call one or more tools)
        function_calls = event.get_function_calls()
        if function_calls:
            for call in function_calls:
                console.print(
                    Panel(
                        f"[bold cyan]Tool:[/bold cyan] {call.name}\n[bold cyan]Arguments:[/bold cyan] {call.args}",
                        title="[bold yellow]🔧 ADK Function Call Triggered[/bold yellow]",
                        border_style="yellow",
                        expand=False,
                    )
                )

        # B. Detect Tool Execution Responses (Live API payload returned to Gemini)
        function_responses = event.get_function_responses()
        if function_responses:
            for resp in function_responses:
                formatted_resp = str(resp.response)
                if len(formatted_resp) > 300:
                    formatted_resp = formatted_resp[:300] + " ... (truncated)"
                console.print(
                    Panel(
                        f"[bold green]Tool:[/bold green] {resp.name}\n[bold green]Payload:[/bold green] {formatted_resp}",
                        title="[bold green]📥 Live Tool Response Returned to Agent[/bold green]",
                        border_style="green",
                        expand=False,
                    )
                )

        # C. Detect Content / Text Generated by the Model
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    accumulated_response.append(part.text)

    # 3. Render the synthesized final response in Markdown
    full_text = "".join(accumulated_response).strip()
    if full_text:
        console.print("\n[bold cyan]🤖 Agent Response:[/bold cyan]")
        console.print(Markdown(full_text))
    else:
        console.print("[dim](Turn finished with no text output)[/dim]")


async def main() -> None:
    """Main interactive execution loop."""
    print_banner()

    # Instantiate the ADK InMemoryRunner
    app_name = "adk_realtime_app"
    runner = InMemoryRunner(agent=root_agent, app_name=app_name)

    # Create a persistent session for multi-turn conversation
    session_id = f"demo_session_{uuid.uuid4().hex[:6]}"
    await runner.session_service.create_session(
        app_name=app_name,
        user_id="presenter_user",
        session_id=session_id,
    )

    console.print(f"[dim]Active Session ID: {session_id} (Preserves multi-turn state across questions)[/dim]\n")

    while True:
        console.print("[bold]Choose an option or type your question:[/bold]")
        for idx, (label, prompt) in enumerate(PRESET_PROMPTS, 1):
            console.print(f"  [bold cyan][{idx}][/bold cyan] [white]{label}[/white]")
            console.print(f"      [dim]\"{prompt}\"[/dim]")
        console.print("  [bold cyan][q][/bold cyan] [white]Quit[/white]")
        console.print()

        try:
            choice = input("Enter option [1-4] or type custom question: ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Exiting demo. Goodbye![/yellow]")
            break

        if not choice:
            continue

        if choice.lower() in ("q", "quit", "exit"):
            console.print("\n[yellow]Exiting demo. Goodbye![/yellow]")
            break

        # Check if user selected one of the presets
        if choice in ("1", "2", "3", "4"):
            selected_prompt = PRESET_PROMPTS[int(choice) - 1][1]
        else:
            selected_prompt = choice

        # Execute the conversational turn
        try:
            await execute_turn(runner, session_id, selected_prompt)
        except Exception as err:
            console.print(f"[bold red]Execution error:[/bold red] {err}")

        console.print("\n" + "─" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
