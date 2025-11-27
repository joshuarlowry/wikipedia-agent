# Tool-Based JSON Mode Redesign (Legacy Notes)

> **Status:** This document describes the original **tool-based JSON mode** implementation.  
> The current system combines this approach with **Strands Structured Output** using a `FactOutput` Pydantic model  
> for the final JSON response, while `record_fact` and `FactAccumulator` continue to support extraction internally.

## Summary

We successfully redesigned the JSON output mode to use a **tool-based fact accumulation approach** instead of forcing the LLM to directly output JSON. This architectural change provides significant benefits in reliability, maintainability, and extensibility.

## Problem with Previous Approach

The original implementation asked the LLM to:
1. Read all Wikipedia articles
2. Extract facts and track sources
3. Format everything as perfect JSON
4. Output only valid JSON with no extra text

**Issues:**
- ❌ LLM had to be both researcher AND data formatter simultaneously
- ❌ Frequent JSON parsing errors (missing brackets, commas, extra text)
- ❌ Cognitively demanding for the LLM
- ❌ No real-time visibility into fact extraction
- ❌ Difficult to extend with new metadata

## New Architecture

### How It Works

1. **LLM Reads Documents**: LLM receives Wikipedia articles naturally, as formatted text
2. **record_fact() Tool**: As the LLM discovers information, it calls `record_fact(fact, source_ids, category)`
3. **Fact Accumulator**: System stores each fact in a `FactAccumulator` object
4. **Programmatic JSON**: After LLM finishes, system generates perfect JSON from accumulated facts

### Key Components

#### 1. FactAccumulator (`src/fact_accumulator.py`)
```python
class FactAccumulator:
    """Accumulates facts as the LLM discovers them."""
    - Stores facts and sources
    - Validates fact categories
    - Generates JSON programmatically
    - Provides summary generation
```

#### 2. record_fact() Tool (`src/wikipedia/tools.py`)
```python
@tool
def record_fact(fact: str, source_ids: List[str], category: str) -> str:
    """Tool that LLM calls to record each discovered fact."""
```

#### 3. Updated search_and_retrieve_articles_json
- Returns articles with clear SOURCE IDs
- Automatically registers sources with accumulator
- Instructs LLM to use record_fact() tool

#### 4. Updated System Prompt
- Instructs LLM to use record_fact() as it reads
- Focuses on extraction, not formatting
- Provides clear examples

## Benefits

### ✅ Guaranteed Valid JSON
- System constructs JSON programmatically
- Eliminates all parsing errors
- Perfect structure every time

### ✅ Separation of Concerns
- LLM focuses on understanding content
- System handles data formatting
- Clear responsibility boundaries

### ✅ Real-Time Tracking
- See facts being extracted live
- Status updates: "💾 Recording facts... (5 recorded)"
- Better visibility into LLM's work

### ✅ More Natural for LLM
- LLM thinks: "I found something, let me record it"
- Similar to how humans take notes
- Reduces cognitive load

### ✅ Easier to Extend
- Want confidence scores? Add parameter to tool
- Want fact relationships? Add link_facts() tool
- Want quotes? Add record_quote() tool
- System remains flexible

## Implementation Details

### Files Created
- `src/fact_accumulator.py` - New module for fact storage and JSON generation

### Files Modified
- `src/agent.py` - Initialize accumulator, return generated JSON
- `src/wikipedia/tools.py` - Added record_fact() tool, updated json tool
- `prompts/system.yaml` - Updated JSON prompt for tool usage
- `test_json_mode.py` - Updated test for new approach
- `demo_json_mode.py` - Updated demo for new approach
- `test_simple.py` - Updated to use WikipediaSearch directly
- `README.md` - Documented tool-based approach
- `JSON_MODE_FEATURE.md` - Complete architecture documentation

### Files Unchanged
- All MLA mode functionality preserved
- No breaking changes to existing API
- All unit tests pass (34 passed, 4 skipped)

## Test Results

### Unit Tests
```bash
$ pytest tests/ -v
============================= test session starts ==============================
34 passed, 4 skipped, 1 warning in 5.68s
```

### Integration Tests
- ✅ Agent initialization
- ✅ Output format switching
- ✅ Wikipedia search
- ✅ Simple integration test

### Test Coverage
- Core modules: 98% (config), 94% (citation), 87% (llm.base)
- New module: 41% (fact_accumulator) - will increase with E2E tests
- Agent: 32% (many paths require real LLM calls)

## Usage Examples

### Python API
```python
from src.agent import WikipediaAgent
from src.config import Config

# Enable JSON mode
config = Config("config.yaml")
config._config["agent"]["output_format"] = "json"

# Create agent
agent = WikipediaAgent(config)

# Query - system handles fact accumulation automatically
response = agent.query("What is quantum computing?", stream=False)

# Response is guaranteed valid JSON
import json
data = json.loads(response)

print(f"Found {len(data['sources'])} sources")
print(f"Extracted {len(data['facts'])} facts")
```

### Demo Script
```bash
python demo_json_mode.py
```

Shows both MLA and JSON modes with side-by-side comparison.

## Future Enhancements

The tool-based approach enables many future features:

1. **Enhanced Metadata**: Add confidence scores, timestamps to facts
2. **Quote Extraction**: Add `record_quote()` tool for verbatim quotes
3. **Fact Relationships**: Add `link_facts()` tool to connect related facts
4. **Real-time Validation**: Validate facts as recorded, not at the end
5. **Clarification Requests**: LLM asks for clarification via tools
6. **Automatic Deduplication**: Merge similar facts from different sources
7. **LLM-Generated Summary**: Add `generate_summary()` tool call at end

## Migration Impact

### For Users
- ✅ No changes needed - MLA mode is default
- ✅ JSON mode works the same externally
- ✅ Better reliability and accuracy

### For Developers
- ✅ No breaking API changes
- ✅ All tests pass
- ✅ More maintainable codebase
- ✅ Easier to extend with new features

## Conclusion

This redesign fundamentally improves the JSON mode architecture by:
- Separating LLM understanding from data formatting
- Guaranteeing valid JSON output
- Enabling real-time fact tracking
- Making the system more extensible

The approach demonstrates how proper tool design can make LLM agents more reliable and maintainable while reducing the cognitive load on the LLM itself.

---

**Date Completed:** 2025-11-23  
**Tests Status:** ✅ All passing (34 passed, 4 skipped)  
**Breaking Changes:** None  
**Documentation:** Complete
