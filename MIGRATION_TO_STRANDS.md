# Migration to Strands Framework

This document describes the migration of the Wikipedia Research Agent from a custom implementation to the Strands Agents framework.

## What Changed

### Architecture

**Before:**
- Custom LLM provider interfaces (`src/llm/base.py`, `ollama.py`, `openrouter.py`)
- Manual agent orchestration in `src/agent.py`
- Direct API calls to LLM providers

**After:**
- Strands Agent framework handles orchestration
- Strands model providers (OllamaModel, LiteLLMModel)
- Wikipedia functionality exposed as Strands tools (`@tool` decorated functions)
- Automatic tool calling and response generation

### Key Files

| File | Status | Description |
|------|--------|-------------|
| `src/agent.py` | **Replaced** | Now uses Strands Agent framework |
| `src/agent_legacy.py` | **New (backup)** | Original custom implementation |
| `src/wikipedia/tools.py` | **New** | Strands tools for Wikipedia search |
| `src/llm/` | **Deprecated** | No longer used (kept for reference) |

### Dependencies Added

```bash
strands-agents[ollama,litellm]>=1.0.0
strands-agents-tools>=0.2.0
```

Installed with:
```bash
uv pip install 'strands-agents[ollama,litellm]>=1.0.0' 'strands-agents-tools>=0.2.0'
```

## Benefits of Strands

1. **Model-Driven Orchestration**: Strands handles the agent loop, state management, and tool calling automatically
2. **Multi-Provider Support**: Easy integration with multiple LLM providers (Ollama, OpenAI via LiteLLM, Bedrock, etc.)
3. **Tool Integration**: Clean `@tool` decorator pattern for exposing functions to the agent
4. **Observability**: Built-in metrics, tracing, and logging
5. **Streaming Support**: Native async streaming capabilities
6. **Community**: Access to strands-agents-tools package with pre-built utilities

## Usage

### Basic Usage (Same API)

The public API remains the same:

```python
from src.agent import WikipediaAgent
from src.config import Config

# Initialize agent
config = Config("config.yaml")
agent = WikipediaAgent(config)

# Query without streaming
response = agent.query("What is quantum computing?", stream=False)
print(response)

# Query with streaming
for chunk in agent.query("What is machine learning?", stream=True):
    print(chunk, end="", flush=True)
```

### Configuration

The config format remains the same, but now uses Strands model providers under the hood:

```yaml
llm:
  provider: "ollama"  # or "openrouter"

  ollama:
    base_url: "http://localhost:11434"
    model: "mistral:latest"  # Must support tool calling!
    temperature: 0.7

  openrouter:
    base_url: "https://openrouter.ai/api/v1"
    api_key_env: "OPENROUTER_API_KEY"
    model: "anthropic/claude-3.5-sonnet"
    temperature: 0.7
```

**Important**: The Ollama model must support tool calling. Models that support tools:
- ✅ `mistral:latest`
- ✅ `llama3.1` and newer
- ✅ `deepseek-r1:8b`
- ❌ `gemma2:2b` (does not support tools)
- ❌ `tinyllama:latest` (does not support tools)

### Wikipedia Tools

Four Strands tools are now available:

1. **`search_wikipedia(query, max_articles=3)`**
   - Search for Wikipedia articles by query
   - Returns article titles and URLs

2. **`get_wikipedia_article(title, max_chars=3000)`**
   - Retrieve a specific article by title
   - Returns content with metadata

3. **`search_and_retrieve_articles(query, max_articles=3, max_chars_per_article=3000)`**
   - Main tool: search and retrieve full articles
   - Includes MLA citations automatically

4. **`format_mla_citation(title)`**
   - Generate MLA 9th edition citation for an article

The agent automatically calls these tools when answering questions.

## Testing

### Quick Test

```bash
# Activate virtual environment
source .venv/bin/activate

# Run test script
python test_strands_agent.py
```

### Run Existing Scripts

The existing CLI and TUI should work without changes:

```bash
# CLI
wikipedia-agent-cli "What is quantum computing?"

# TUI
wikipedia-agent
```

## Troubleshooting

### Error: "does not support tools"

**Problem**: The Ollama model doesn't support tool calling.

**Solution**: Update `config.yaml` to use a model with tool support:
```yaml
model: "mistral:latest"  # or llama3.1, deepseek-r1:8b
```

### ImportError: No module named 'strands'

**Problem**: Strands dependencies not installed.

**Solution**:
```bash
uv pip install 'strands-agents[ollama,litellm]>=1.0.0' 'strands-agents-tools>=0.2.0'
```

### Connection errors with Ollama

**Problem**: Ollama server not running.

**Solution**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

## Rollback to Legacy Implementation

If you need to revert to the original implementation:

```python
# Import the legacy agent
from src.agent_legacy import WikipediaAgent

# Use exactly as before
agent = WikipediaAgent(config)
response = agent.query("Your question")
```

The legacy implementation is preserved in `src/agent_legacy.py`.

## Next Steps

1. **Try it out**: Run `python test_strands_agent.py` to see it in action
2. **Explore**: Check `src/wikipedia/tools.py` to see how tools are defined
3. **Extend**: Add more tools using the `@tool` decorator pattern
4. **Monitor**: Use Strands' built-in metrics and tracing for observability

## Resources

- **Strands Documentation**: https://strandsagents.com/latest/
- **Strands Quickstart**: https://strandsagents.com/latest/documentation/docs/user-guide/quickstart/
- **Ollama Configuration**: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/ollama/
- **LiteLLM Configuration**: https://strandsagents.com/latest/documentation/docs/user-guide/concepts/model-providers/litellm/
- **GitHub**: https://github.com/strands-agents/sdk-python

## Summary

The migration to Strands provides a more robust, scalable foundation for the Wikipedia Research Agent while maintaining backward compatibility with the existing API. The new architecture makes it easier to add features, support new providers, and benefit from the Strands ecosystem.
