# Testing Guide

This project has multiple levels of testing to ensure quality while minimizing API costs.

## Automated CI Tests (Free & Fast)

Run automatically on every push/PR via GitHub Actions:

```bash
# Run locally to match CI:
pytest tests/ -v --cov=src
python test_integration_mocked.py
```

**What's tested:**
- ✅ Unit tests with mocked responses
- ✅ Agent initialization
- ✅ Configuration loading
- ✅ Output format switching (MLA/JSON)
- ✅ Basic query flow with mocked LLM

**Cost:** $0 (no API calls)
**Time:** ~30 seconds

## Manual E2E Tests (Real API Calls)

Run manually when you want to verify everything works end-to-end with real LLM APIs:

```bash
# Test both modes
python test_e2e_manual.py

# Test only markdown mode
python test_e2e_manual.py --markdown

# Test only JSON mode
python test_e2e_manual.py --json
```

**What's tested:**
- ✅ Real API calls to OpenRouter/Ollama
- ✅ Wikipedia search and retrieval
- ✅ Markdown/MLA citation formatting
- ✅ JSON structured output
- ✅ Complete query flow

**Cost:** ~$0.01-0.02 per test run (OpenRouter)
**Time:** ~30-60 seconds per test

⚠️ **Warning:** These tests make real API calls! Make sure you have:
1. Configured your LLM provider in `config.yaml`
2. Set `OPENROUTER_API_KEY` in `.env` (if using OpenRouter)
3. Started Ollama service (if using Ollama)

## Existing Test Scripts

The repository also includes standalone test scripts:

### Basic Functionality Test
```bash
python test_simple.py
```
Tests Wikipedia search and agent initialization without making LLM calls.

### JSON Mode Test
```bash
python test_json_mode.py
```
Tests both MLA and JSON output modes with real API calls.

### Strands Agent Test
```bash
python test_strands_agent.py
```
Tests the Strands framework integration.

## Writing New Tests

### Unit Tests (Preferred)

Add to `tests/` directory with mocked LLM responses:

```python
from unittest.mock import Mock, patch
from src.agent import WikipediaAgent

def test_my_feature():
    with patch.object(agent.agent, '__call__', return_value=Mock(output="...")):
        result = agent.query("test")
        assert "expected" in result
```

### Manual E2E Tests

Only add when absolutely necessary. Keep queries short to minimize API costs:

```python
# Good: Short, focused query
question = "What is Python?"

# Bad: Long, expensive query
question = "Explain in detail the complete history..."
```

## CI Configuration

The GitHub Actions workflow (`.github/workflows/tests.yml`) runs:

1. **Unit tests** - Fast, free, comprehensive
2. **Integration tests** - Mocked LLM, no API calls

**Removed from CI:**
- ❌ Real API calls (moved to manual testing)
- ❌ E2E tests with OpenRouter (too expensive)

This keeps CI:
- ✅ Fast (< 2 minutes)
- ✅ Free (no API costs)
- ✅ Reliable (no LLM variability)

## Testing Best Practices

1. **Mock by default** - Use real APIs only when necessary
2. **Keep queries short** - Minimize token usage in E2E tests
3. **Test locally first** - Don't waste CI credits on broken code
4. **Document costs** - Note when tests make paid API calls
5. **Separate concerns** - Unit test logic, E2E test integration

## Coverage

Current test coverage: Run `pytest --cov=src --cov-report=html` to see detailed coverage report in `htmlcov/index.html`.

Target coverage: >80% for core modules (`agent.py`, `config.py`, `wikipedia/`)
