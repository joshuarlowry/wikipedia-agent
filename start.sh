#!/usr/bin/env bash
# Start script for Wikipedia Research Agent

set -e  # Exit on error

echo "Wikipedia Research Agent - Starting..."
echo "======================================"
echo ""

# Check if Ollama is running
echo "Checking Ollama connection at localhost:11434..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
else
    echo "✗ Error: Ollama is not responding on localhost:11434"
    echo "  Please make sure Ollama is running with: systemctl start ollama"
    echo "  Or start it manually"
    exit 1
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "✗ Error: Virtual environment not found"
    echo "  Please run: uv venv && uv pip install -e ."
    exit 1
fi
echo ""

# Check if dependencies are installed
if ! python -c "import src.tui.app" 2>/dev/null; then
    echo "Installing dependencies..."
    uv pip install -e .
fi

echo "Starting Wikipedia Research Agent TUI..."
echo "======================================"
echo ""
echo "Keyboard shortcuts:"
echo "  Enter    - Submit question"
echo "  Ctrl+N   - New question"
echo "  Ctrl+L   - Clear response"
echo "  F1       - Help"
echo "  Ctrl+C   - Quit"
echo ""

# Start the TUI application
python -m src.tui.app
