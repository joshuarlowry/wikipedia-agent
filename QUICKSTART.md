# Quick Start Guide

Get up and running with Wikipedia Research Agent in minutes!

## Step 1: Install Dependencies

```bash
# Clone or navigate to the project
cd wikipedia-agent

# Create virtual environment and install
uv venv
uv pip install -e .
```

## Step 2: Configure LLM Provider

Choose one of the following options:

### Option A: Ollama (Local, Free)

1. Install Ollama from https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Edit `config.yaml`:
   ```yaml
   llm:
     provider: "ollama"
     ollama:
       model: "llama3.2"
   ```

### Option B: OpenRouter (Cloud, Requires API Key)

1. Get an API key from https://openrouter.ai
2. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
3. Add your API key to `.env`:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
4. Edit `config.yaml`:
   ```yaml
   llm:
     provider: "openrouter"
     openrouter:
       model: "anthropic/claude-3.5-sonnet"
   ```

## Step 3: Launch the TUI

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the application
wikipedia-agent
```

## Step 4: Ask Questions!

1. Type your question in the input field
2. Press Enter
3. Watch as Wikipedia articles are found
4. Get a comprehensive answer with MLA citations

## Keyboard Shortcuts

- `Enter` - Submit question
- `Ctrl+N` - New question
- `Ctrl+L` - Clear screen
- `F1` - Show help
- `Ctrl+C` - Quit

## Troubleshooting

### "LLM provider is not available"

**Using Ollama:**
- Make sure Ollama is running: `ollama serve`
- Verify the model is installed: `ollama list`

**Using OpenRouter:**
- Check your API key is correct in `.env`
- Verify you have credits on your OpenRouter account

### "No Wikipedia articles found"

- Try rephrasing your question
- Use more specific terms
- Check your internet connection

### TUI looks broken

- Make sure your terminal supports colors
- Try resizing your terminal window
- Some terminals may not support all features

## Example Questions to Try

- "What is quantum computing?"
- "Explain the history of the Internet"
- "How does photosynthesis work?"
- "What is machine learning?"
- "Describe the water cycle"

## Next Steps

- Customize prompts in `prompts/system.yaml`
- Adjust Wikipedia search parameters in `config.yaml`
- Try different LLM models
- Use the CLI for automation: `wikipedia-agent-cli "your question"`

Enjoy researching with AI! 🚀
