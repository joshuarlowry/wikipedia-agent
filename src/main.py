"""Main entry point for the Wikipedia agent CLI."""

import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from rich.live import Live

from .agent import WikipediaAgent
from .config import Config


console = Console()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wikipedia Research Agent with LLM integration (Strands-powered)"
    )
    parser.add_argument("query", type=str, help="Your research question")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON instead of MLA-formatted text",
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config = Config(args.config)
        # Override output format if --json flag is provided
        if args.json:
            config._config["agent"]["output_format"] = "json"
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
        sys.exit(1)

    # Initialize agent
    try:
        agent = WikipediaAgent(config)
    except Exception as e:
        console.print(f"[red]Error initializing agent: {e}[/red]")
        sys.exit(1)

    # Check if agent is ready
    if not agent.is_ready:
        console.print("[red]LLM provider is not available. Please check your configuration.[/red]")
        sys.exit(1)

    # Display query
    console.print(Panel(f"[bold cyan]Question:[/bold cyan] {args.query}", expand=False))
    console.print()

    # Set up status callback to show progress
    def status_callback(message: str):
        console.print(f"[dim]{message}[/dim]")
    
    agent.set_status_callback(status_callback)

    try:
        if args.no_stream:
            # Non-streaming
            console.print()
            response = agent.query(args.query, stream=False)
            console.print()
            # Display response based on output format
            if args.json:
                # For JSON, print as-is without Markdown formatting
                console.print(response)
            else:
                console.print(Markdown(response))
        else:
            # Streaming
            console.print()
            response_text = ""
            for chunk in agent.query(args.query, stream=True):
                response_text += chunk
                console.print(chunk, end="", highlight=False)
            console.print()

    except Exception as e:
        console.print(f"\n[red]Error generating response: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)

    console.print()


if __name__ == "__main__":
    main()
