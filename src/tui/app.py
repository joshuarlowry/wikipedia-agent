"""Main TUI application for Wikipedia Research Agent."""

import sys
import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Input, RichLog, Button
from textual.binding import Binding
from textual.reactive import reactive
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from ..agent import WikipediaAgent
from ..config import Config


class ArticleList(Static):
    """Widget to display found Wikipedia articles."""

    articles = reactive([])

    def render(self) -> Panel:
        """Render the article list."""
        if not self.articles:
            content = Text("No articles loaded yet.", style="dim")
        else:
            lines = []
            for i, article in enumerate(self.articles, 1):
                lines.append(f"{i}. {article.title}")
                lines.append(f"   {article.word_count} words • {article.url}")
                if i < len(self.articles):
                    lines.append("")
            content = "\n".join(lines)

        return Panel(
            content,
            title="[bold cyan]Wikipedia Articles[/bold cyan]",
            border_style="cyan",
        )


class ResponseDisplay(RichLog):
    """Widget to display LLM responses with streaming support."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.can_focus = False
        self.auto_scroll = True


class StatusBar(Static):
    """Status bar showing agent configuration."""

    provider = reactive("Unknown")
    model = reactive("Unknown")
    status = reactive("Ready")

    def render(self) -> Text:
        """Render the status bar."""
        text = Text()
        text.append("Provider: ", style="bold")
        text.append(self.provider, style="cyan")
        text.append(" | Model: ", style="bold")
        text.append(self.model, style="green")
        text.append(" | Status: ", style="bold")

        if self.status == "Ready":
            text.append(self.status, style="green")
        elif self.status == "Searching":
            text.append(self.status, style="yellow")
        elif self.status == "Generating":
            text.append(self.status, style="blue")
        else:
            text.append(self.status, style="red")

        return text


class WikipediaAgentApp(App):
    """Wikipedia Research Agent TUI Application."""

    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
    }

    #left-panel {
        width: 40%;
        height: 100%;
        border: solid $primary;
    }

    #right-panel {
        width: 60%;
        height: 100%;
    }

    #article-list {
        height: 1fr;
        margin: 1;
    }

    #response-container {
        height: 1fr;
        border: solid $accent;
        margin: 1;
    }

    #response-display {
        height: 1fr;
        background: $surface-darken-1;
        border: solid $primary;
        margin: 1;
        padding: 1;
    }

    #input-container {
        height: auto;
        margin: 1;
        padding: 1;
        background: $surface-lighten-1;
        border: solid $accent;
    }

    #question-input {
        width: 100%;
    }

    #status-bar {
        height: 1;
        background: $surface-darken-2;
        color: $text;
        padding: 0 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+n", "new_question", "New Question"),
        Binding("ctrl+l", "clear_response", "Clear"),
        ("f1", "help", "Help"),
    ]

    TITLE = "Wikipedia Research Agent"

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the TUI app."""
        super().__init__()
        self.config = Config(config_path)
        self.agent = WikipediaAgent(self.config)
        self.current_articles = []

    def compose(self) -> ComposeResult:
        """Compose the UI layout."""
        yield Header()

        with Container(id="main-container"):
            with Horizontal():
                # Left panel: Articles
                with Vertical(id="left-panel"):
                    yield ArticleList(id="article-list")

                # Right panel: Response and input
                with Vertical(id="right-panel"):
                    with Container(id="response-container"):
                        yield Static(
                            "[bold cyan]Response[/bold cyan]",
                            id="response-header"
                        )
                        yield ResponseDisplay(id="response-display")

                    with Container(id="input-container"):
                        yield Static(
                            "[bold]Ask a question:[/bold]",
                            id="input-label"
                        )
                        yield Input(
                            placeholder="What would you like to know?",
                            id="question-input"
                        )

        yield StatusBar(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Handle app mount."""
        # Set initial status
        status_bar = self.query_one("#status-bar", StatusBar)
        status_bar.provider = self.config.llm_provider

        if self.config.llm_provider == "ollama":
            status_bar.model = self.config.ollama_config.get("model", "unknown")
        else:
            status_bar.model = self.config.openrouter_config.get("model", "unknown")

        # Check if agent is ready
        if not self.agent.is_ready:
            status_bar.status = "Error: LLM not available"
            self.notify(
                "LLM provider is not available. Please check your configuration.",
                severity="error",
                timeout=10,
            )
        else:
            status_bar.status = "Ready"

        # Focus the input
        self.query_one("#question-input", Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle question submission."""
        question = event.value.strip()
        if not question:
            return

        # Clear input
        event.input.value = ""

        # Process the question
        await self.process_question(question)

    async def process_question(self, question: str) -> None:
        """Process a question by searching Wikipedia and generating a response."""
        status_bar = self.query_one("#status-bar", StatusBar)
        response_display = self.query_one("#response-display", ResponseDisplay)
        article_list = self.query_one("#article-list", ArticleList)

        # Clear previous response
        response_display.clear()

        # Search Wikipedia
        status_bar.status = "Searching"
        self.notify("Searching Wikipedia...", timeout=2)

        try:
            # Search in background using asyncio.to_thread
            articles = await asyncio.to_thread(self.agent.search_wikipedia, question)

            if not articles:
                status_bar.status = "Ready"
                response_display.write(
                    Panel(
                        "[yellow]No Wikipedia articles found for your query.[/yellow]",
                        title="No Results"
                    )
                )
                self.notify("No articles found", severity="warning")
                return

            # Update article list
            self.current_articles = articles
            article_list.articles = articles
            self.notify(f"Found {len(articles)} article(s)", timeout=2)

            # Generate response
            status_bar.status = "Generating"
            response_display.write(
                Panel(
                    f"[bold cyan]Question:[/bold cyan] {question}",
                    border_style="cyan"
                )
            )
            response_display.write("")

            # Stream the response in a background thread
            def get_chunks():
                """Collect all chunks from the LLM stream."""
                return list(self.agent.stream_response(question, articles))

            chunks = await asyncio.to_thread(get_chunks)
            for chunk in chunks:
                response_display.write(chunk)

            status_bar.status = "Ready"
            self.notify("Response complete", severity="information", timeout=2)

        except Exception as e:
            status_bar.status = "Error"
            response_display.write(
                Panel(
                    f"[red]Error: {str(e)}[/red]",
                    title="Error",
                    border_style="red"
                )
            )
            self.notify(f"Error: {str(e)}", severity="error", timeout=5)

    def action_new_question(self) -> None:
        """Focus the input for a new question."""
        input_widget = self.query_one("#question-input", Input)
        input_widget.value = ""
        input_widget.focus()

    def action_clear_response(self) -> None:
        """Clear the response display."""
        response_display = self.query_one("#response-display", ResponseDisplay)
        response_display.clear()
        self.notify("Response cleared", timeout=1)

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
# Wikipedia Research Agent - Help

## How to Use

1. Type your question in the input field at the bottom
2. Press Enter to submit
3. Wait for Wikipedia articles to be found
4. The AI will generate a response with MLA citations

## Keyboard Shortcuts

- **Enter**: Submit question
- **Ctrl+N**: Clear input for new question
- **Ctrl+L**: Clear response display
- **Ctrl+C**: Quit application
- **F1**: Show this help

## Features

- Searches Wikipedia for relevant articles
- Generates comprehensive answers using AI
- Automatically includes MLA format citations
- Streaming responses for real-time feedback

## Configuration

Edit `config.yaml` to change:
- LLM provider (Ollama or OpenRouter)
- Model selection
- Wikipedia search parameters
        """
        response_display = self.query_one("#response-display", ResponseDisplay)
        response_display.clear()
        response_display.write(Markdown(help_text))


def main():
    """Main entry point for the TUI."""
    config_path = "config.yaml"

    # Check for custom config path in args
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    app = WikipediaAgentApp(config_path)
    app.run()


if __name__ == "__main__":
    main()
