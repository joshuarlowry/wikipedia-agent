# GitHub CI Setup

This document describes the CI/CD setup for the Wikipedia Agent project.

## Overview

The CI pipeline is designed to be **fast, free, and reliable** by avoiding expensive API calls while still providing comprehensive test coverage.

## Workflow: `.github/workflows/tests.yml`

### Triggers
- Push to `main`, `master`, or `develop` branches
- Pull requests to those branches
- Manual dispatch via GitHub Actions UI

### Jobs

#### 1. Unit Tests
```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```
- Runs all unit tests in `tests/` directory
- Generates coverage report
- **No API calls** - all external dependencies are mocked

#### 2. Integration Tests (Mocked)
```bash
python test_integration_mocked.py
```
- Tests agent initialization with mocked LLM
- Tests configuration management
- Tests output format switching (MLA/JSON)
- Tests query flow with mocked responses
- **No credentials required** - model creation is mocked

### Key Design Decisions

✅ **No API Calls in CI**
- All LLM API calls are mocked using `unittest.mock`
- Model initialization is patched to avoid authentication
- Zero cost per CI run

✅ **No Secrets Required**
- CI doesn't need `OPENROUTER_API_KEY` secret
- Tests run successfully without any credentials
- Faster setup for contributors

✅ **Fast Execution**
- Target: < 2 minutes total
- No network latency from API calls
- Predictable, consistent runtime

✅ **Reliable Results**
- No LLM variability in test outputs
- No API rate limiting issues
- No external service dependencies

## Dependencies

### Required in CI
- Python 3.11
- `uv` package manager (for fast dependency installation)
- All packages in `pyproject.toml`

### Not Required in CI
- ❌ OpenRouter API key
- ❌ Ollama service
- ❌ Any LLM provider credentials

## Manual Testing

For end-to-end testing with real API calls, use the manual test script:

```bash
python test_e2e_manual.py
```

See [TESTING.md](../../TESTING.md) for full testing guide.

## Updating CI

### Adding New Tests

**For unit tests (preferred):**
```python
# Add to tests/ directory
def test_new_feature():
    with patch('src.module.external_call'):
        result = my_function()
        assert result == expected
```

**For integration tests:**
```python
# Add to test_integration_mocked.py
def test_new_integration():
    with patch('src.agent.create_model_from_config') as mock_model:
        mock_model.return_value = Mock()
        # Your test here
```

### Modifying Workflow

Edit `.github/workflows/tests.yml` and update:
- Job steps
- Environment variables
- Test commands

**Important:** Keep all tests mocked to avoid API costs!

## Troubleshooting

### "401 Unauthorized" errors in CI
- This shouldn't happen if mocking is correct
- Check that `create_model_from_config` is patched
- Verify no real API calls are being made

### Tests pass locally but fail in CI
- Check for environment-specific assumptions
- Verify all external dependencies are mocked
- Ensure no hardcoded paths

### Slow CI execution
- Target is < 2 minutes
- Check for unmocked network calls
- Review test parallelization

## Cost Analysis

| Test Type | Cost per Run | Time | When to Use |
|-----------|-------------|------|-------------|
| CI (mocked) | $0 | ~1-2 min | Every commit |
| Manual E2E | ~$0.01-0.02 | ~1-2 min | Before release |

**Annual CI cost estimate:** $0 (all tests are mocked)

## Future Improvements

Potential enhancements:
- [ ] Add performance benchmarking
- [ ] Add security scanning (Dependabot)
- [ ] Add linting checks (ruff, black)
- [ ] Add type checking (mypy)
- [ ] Matrix testing across Python versions
- [ ] Automated release on tag push
