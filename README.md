# Wikipedia Research Agent

A Wikipedia research agent powered by the **[Strands Agents framework](https://strandsagents.com/)** with an interactive Terminal UI that searches for relevant articles, synthesizes information using LLMs, and provides responses with proper MLA citations.

> **Note**: This project has been migrated to use the Strands Agents SDK for improved orchestration, multi-provider support, and better observability. See [MIGRATION_TO_STRANDS.md](MIGRATION_TO_STRANDS.md) for details.

## Features

- **Strands-Powered**: Built on the [Strands Agents SDK](https://strandsagents.com/) for robust agent orchestration
- **Interactive TUI**: Beautiful terminal interface with real-time updates
- **Wikipedia Tools**: Strands tools for searching, retrieving, and citing Wikipedia articles
- **Multiple LLM Backends**: Support for Ollama (local), OpenRouter (cloud), and more via Strands
- **Dual Output Modes**: 
  - **MLA Mode**: Comprehensive responses with properly formatted MLA 9th edition citations
  - **JSON Mode**: Structured data with sources, facts, and references for programmatic use
- **Configurable**: YAML-based configuration with environment variable support
- **Streaming Support**: Real-time streaming responses from LLMs
- **Template System**: Customizable prompts with citation enforcement

## Installation

```bash
# Using pip
pip install -e .

# Or using uv (recommended)
uv venv
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

## Configuration

1. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

2. Edit `config.yaml` to configure your LLM provider:

```yaml
llm:
  provider: "ollama"  # or "openrouter"

  ollama:
    base_url: "http://localhost:11434"
    model: "llama3.2"
    temperature: 0.7

  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: "OPENROUTER_API_KEY"
    model: "anthropic/claude-3.5-sonnet"
    temperature: 0.7

wikipedia:
  language: "en"
  max_articles: 3
  max_chars_per_article: 3000

agent:
  stream_response: true
  enforce_citations: true
  output_format: "mla"  # mla | json
```

### Output Formats

The agent supports two output formats:

#### MLA Format (Default)
Returns a comprehensive narrative response with proper MLA 9th edition citations.

```yaml
agent:
  output_format: "mla"
```

Example output:
```
Quantum computing is a revolutionary approach to computation that leverages
quantum mechanical phenomena like superposition and entanglement...

Works Cited
"Quantum Computing." Wikipedia, Wikimedia Foundation, 15 Nov. 2024,
    en.wikipedia.org/wiki/Quantum_computing. Accessed 22 Nov. 2025.
```

#### JSON Format
Returns structured data with sources and facts, ideal for programmatic use.

```yaml
agent:
  output_format: "json"
```

Example output:
```json
{
  "query": "What is quantum computing?",
  "sources": [
    {
      "id": "source_1",
      "title": "Quantum computing",
      "url": "https://en.wikipedia.org/wiki/Quantum_computing",
      "last_modified": "2024-11-15",
      "word_count": 5000
    }
  ],
  "facts": [
    {
      "fact": "Quantum computing uses quantum bits (qubits) which can exist in superposition",
      "source_ids": ["source_1"],
      "category": "definition"
    },
    {
      "fact": "Quantum computers can solve certain problems exponentially faster than classical computers",
      "source_ids": ["source_1", "source_2"],
      "category": "application"
    }
  ],
  "summary": "Quantum computing leverages quantum mechanical phenomena to perform computations. It uses qubits that can exist in superposition, enabling exponential speedup for specific problems."
}
```

## Usage

### Terminal UI (Default)

Launch the interactive TUI:

```bash
# Using the installed command
wikipedia-agent

# Or with Python
python -m src.tui.app

# With custom config
wikipedia-agent custom-config.yaml
```

**TUI Keyboard Shortcuts:**
- `Enter` - Submit question
- `Ctrl+N` - New question (clear input)
- `Ctrl+L` - Clear response display
- `F1` - Show help
- `Ctrl+C` - Quit

### Command Line Interface

For non-interactive use:

```bash
# Using the CLI command
wikipedia-agent-cli "What is quantum computing?"

# With custom config
wikipedia-agent-cli "Explain photosynthesis" --config custom-config.yaml

# Non-streaming mode
wikipedia-agent-cli "History of Python" --no-stream
```

### Python API

```python
from src.agent import WikipediaAgent
from src.config import Config

# Initialize agent
config = Config("config.yaml")
agent = WikipediaAgent(config)

# Query with streaming
for chunk in agent.query("What is machine learning?", stream=True):
    print(chunk, end="", flush=True)

# Query without streaming
response = agent.query("What is artificial intelligence?", stream=False)
print(response)

# Use JSON mode
from src.config import Config
config = Config("config.yaml")
config._config["agent"]["output_format"] = "json"
json_agent = WikipediaAgent(config)
json_response = json_agent.query("What is machine learning?", stream=False)
print(json_response)  # Returns structured JSON
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_wikipedia.py
```

## Project Structure

```
wikipedia-agent/
├── pyproject.toml          # Project dependencies
├── config.yaml             # Configuration file
├── .env                    # Environment variables
├── prompts/
│   └── system.yaml         # Prompt templates
├── src/
│   ├── agent.py            # Core agent logic
│   ├── config.py           # Configuration management
│   ├── prompts.py          # Prompt template loader
│   ├── main.py             # CLI interface
│   ├── tui/
│   │   ├── __init__.py
│   │   └── app.py          # Terminal UI application
│   ├── wikipedia/
│   │   ├── search.py       # Wikipedia search
│   │   └── citation.py     # MLA citation generator
│   └── llm/
│       ├── base.py         # LLM provider interface
│       ├── ollama.py       # Ollama implementation
│       └── openrouter.py   # OpenRouter implementation
└── tests/
    ├── test_wikipedia.py   # Wikipedia tests
    ├── test_llm.py         # LLM provider tests
    ├── test_agent.py       # Agent workflow tests
    └── test_config.py      # Config tests
```

## TUI Interface

The Terminal UI provides an intuitive interface with:

**Left Panel - Wikipedia Articles:**
- List of found articles with word counts
- Direct links to source articles
- Updates in real-time during search

**Right Panel - Response & Input:**
- Streaming LLM responses with markdown formatting
- Question input field at the bottom
- MLA citations included automatically

**Status Bar:**
- Current LLM provider and model
- Real-time status (Ready, Searching, Generating, Error)

**Features:**
- Real-time streaming responses
- Markdown rendering for better readability
- Keyboard shortcuts for quick navigation
- Help screen accessible via F1

## Example Output

```
Question: What is quantum computing?

[Searching Wikipedia...]
Found 3 articles:
• Quantum computing
• Qubit
• Quantum algorithm

[Generating response...]

Quantum computing is a revolutionary approach to computation that leverages
quantum mechanical phenomena like superposition and entanglement to perform
calculations. Unlike classical computers that use bits representing 0 or 1,
quantum computers use qubits which can exist in multiple states simultaneously...

Works Cited
"Quantum Computing." Wikipedia, Wikimedia Foundation, en.wikipedia.org/wiki/
    Quantum_computing. Accessed 21 Nov. 2025.
"Qubit." Wikipedia, Wikimedia Foundation, en.wikipedia.org/wiki/Qubit.
    Accessed 21 Nov. 2025.
```

## LLM Provider Setup

### Ollama (Local)

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.2`
3. Start Ollama service
4. Set provider to "ollama" in config.yaml

### OpenRouter (Cloud)

1. Get API key from https://openrouter.ai
2. Add key to `.env` as `OPENROUTER_API_KEY`
3. Set provider to "openrouter" in config.yaml

## License

MIT
