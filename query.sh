#!/usr/bin/env bash
# Simple CLI query script for Wikipedia Agent

set -e

# Check if query provided
if [ $# -eq 0 ]; then
    echo "Usage: ./query.sh \"your question here\""
    echo ""
    echo "Examples:"
    echo "  ./query.sh \"What is photosynthesis?\""
    echo "  ./query.sh \"Explain quantum computing\""
    exit 1
fi

# Activate venv
source .venv/bin/activate

# Run the CLI
echo "Wikipedia Research Agent - CLI"
echo "==============================="
echo ""

python -m src.main "$@"
