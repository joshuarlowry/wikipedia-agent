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
        description="Wikipedia Research Agent with LLM integration"
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

    args = parser.parse_args()

    # Load configuration
    try:
        config = Config(args.config)
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

    # Search Wikipedia
    with console.status("[bold green]Searching Wikipedia...", spinner="dots"):
        try:
            articles = agent.search_wikipedia(args.query)
        except Exception as e:
            console.print(f"[red]Error searching Wikipedia: {e}[/red]")
            sys.exit(1)

    if not articles:
        console.print("[yellow]No Wikipedia articles found for your query.[/yellow]")
        sys.exit(0)

    # Display found articles
    console.print("[bold green]Found articles:[/bold green]")
    for article in articles:
        console.print(f"  • {article.title} ({article.word_count} words)")
    console.print()

    # Generate response
    console.print("[bold green]Generating response...[/bold green]")
    console.print()

    try:
        if args.no_stream:
            # Non-streaming
            with console.status("[bold green]Generating...", spinner="dots"):
                response = agent.generate_response(args.query, articles)
            console.print(Markdown(response))
        else:
            # Streaming
            response_text = ""
            for chunk in agent.stream_response(args.query, articles):
                response_text += chunk
                console.print(chunk, end="", highlight=False)
            console.print()

    except Exception as e:
        console.print(f"\n[red]Error generating response: {e}[/red]")
        sys.exit(1)

    console.print()


if __name__ == "__main__":
    main()
