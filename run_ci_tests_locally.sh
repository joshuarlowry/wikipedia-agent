#!/bin/bash
# Run CI tests locally to verify before pushing
# This script mimics what GitHub Actions will run

set -e  # Exit on error

echo "=========================================="
echo "Running CI Tests Locally"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    exit 1
fi

# Test 1: Unit tests with pytest
echo "=========================================="
echo "Test 1: Unit Tests (pytest)"
echo "=========================================="
if command -v pytest &> /dev/null; then
    pytest tests/ -v --cov=src --cov-report=term-missing
    echo -e "${GREEN}✓ Unit tests passed${NC}"
else
    echo -e "${RED}⚠ pytest not found, skipping unit tests${NC}"
    echo "  Install with: pip install pytest pytest-cov"
fi

echo ""
echo "=========================================="
echo "Test 2: Integration Tests (mocked)"
echo "=========================================="
if [ -f "test_integration_mocked.py" ]; then
    python3 test_integration_mocked.py
    echo -e "${GREEN}✓ Integration tests passed${NC}"
else
    echo -e "${RED}✗ test_integration_mocked.py not found${NC}"
    exit 1
fi

echo ""
echo "=========================================="
echo "All CI Tests Passed! ✨"
echo "=========================================="
echo ""
echo "Your code is ready to push!"
echo ""
echo "Optional: Run manual E2E tests with real API:"
echo "  python3 test_e2e_manual.py"
echo ""
