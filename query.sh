#!/usr/bin/env bash
# Simple CLI query script for Wikipedia Agent

set -e

# Check if query provided
if [ $# -eq 0 ]; then
    echo "Usage: ./query.sh [OPTIONS] \"your question here\""
    echo ""
    echo "Options:"
    echo "  --json        Output structured JSON instead of MLA-formatted text"
    echo "  --no-stream   Disable streaming output"
    echo "  --config PATH Use custom config file"
    echo ""
    echo "Examples:"
    echo "  ./query.sh \"What is photosynthesis?\""
    echo "  ./query.sh --json \"Explain quantum computing\""
    echo "  ./query.sh --no-stream \"Tell me about black holes\""
    exit 1
fi

# Activate venv
source .venv/bin/activate

# Run the CLI
echo "Wikipedia Research Agent - CLI"
echo "==============================="
echo ""

python -m src.main "$@"
