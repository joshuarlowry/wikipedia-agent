# JSON Output Mode Feature

## Overview

The Wikipedia Agent now supports two output formats:

1. **MLA Mode** (default): Returns narrative responses with proper MLA 9th edition citations
2. **JSON Mode** (new): Returns structured data with sources, facts, and references using a tool-based fact accumulation approach

## Architecture: Tool-Based Fact Accumulation

JSON mode uses an innovative approach that separates concerns:

### How It Works

1. **LLM Reads Documents**: The LLM receives Wikipedia articles and reads through them naturally
2. **record_fact() Tool**: As the LLM discovers important information, it calls the `record_fact()` tool for each fact
3. **Fact Accumulator**: The system stores each fact in a `FactAccumulator` object
4. **Programmatic JSON Generation**: After the LLM finishes, the system generates perfect JSON from accumulated facts

### Benefits of This Approach

✅ **Guaranteed Valid JSON**: We construct JSON programmatically, eliminating parsing errors  
✅ **Separation of Concerns**: LLM focuses on understanding content, system handles formatting  
✅ **Real-Time Tracking**: We can monitor facts being extracted as they happen  
✅ **More Natural**: LLM operates like "I found something interesting, let me record it"  
✅ **Easier to Extend**: Want to add confidence scores? Just add a parameter to the tool  

### Why Not Ask LLM to Output JSON Directly?

The previous approach forced the LLM to:
- Read all documents
- Extract facts
- Track sources
- Format everything as perfect JSON
- All in one response

This is cognitively demanding and error-prone. The LLM had to be both researcher AND data formatter simultaneously, often leading to:
- Malformed JSON
- Missing brackets or commas
- Extra text before/after JSON
- Parsing failures

## What Changed

### 1. Configuration (`config.yaml`)
Added `output_format` option to agent configuration:

```yaml
agent:
  stream_response: true
  enforce_citations: true
  output_format: "mla"  # Options: "mla" | "json"
```

### 2. System Prompts (`prompts/system.yaml`)
Updated `system_prompt_json` to instruct the LLM to:
- Read through Wikipedia articles carefully
- Use the `record_fact()` tool for each important piece of information
- Link each fact to its source(s) using source_ids
- Categorize facts (definition, history, application, technical, other)
- Focus on extraction, not formatting

### 3. Fact Accumulator (`src/fact_accumulator.py`)
New module that manages fact collection:
- `FactAccumulator` class stores facts as they're discovered
- `Fact` and `Source` dataclasses for type safety
- `record_fact()` method for LLM to call via tool
- `to_json()` method for programmatic JSON generation

### 4. Wikipedia Tools (`src/wikipedia/tools.py`)
Updated and added tools for JSON mode:
- `search_and_retrieve_articles_json`: Returns articles with SOURCE IDs for referencing
- `record_fact`: New tool that LLM calls to save each discovered fact
- Tools automatically register sources with the fact accumulator
- Exports separate tool list `wikipedia_tools_json` for JSON mode

### 4. Configuration Manager (`src/config.py`)
Added `output_format` property to access the configured mode

### 5. Agent (`src/agent.py`)
- Detects output format from configuration
- Initializes `FactAccumulator` for JSON mode queries
- Selects appropriate tools (MLA or JSON) based on mode
- Uses different system prompts for each mode
- Returns accumulated facts as JSON for JSON mode
- Tracks fact recording progress in status updates

### 6. Configuration Manager (`src/config.py`)
- No changes needed - `output_format` property already supported

### 7. Documentation (`README.md`)
Updated comprehensive documentation with:
- Tool-based fact accumulation architecture
- Feature description
- Configuration examples
- Output format examples
- Python API usage examples

## JSON Output Structure

The JSON mode returns structured data in the following format:

```json
{
  "query": "the original question",
  "sources": [
    {
      "id": "source_1",
      "title": "Article Title",
      "url": "https://en.wikipedia.org/wiki/Article_Title",
      "last_modified": "2024-11-15",
      "word_count": 5000
    }
  ],
  "facts": [
    {
      "fact": "A clear, specific piece of information",
      "source_ids": ["source_1", "source_2"],
      "category": "definition"
    }
  ],
  "summary": "A brief 2-3 sentence overview based on all facts"
}
```

### Fields Explained

- **query**: The original user question
- **sources**: Array of source metadata
  - `id`: Unique identifier for referencing
  - `title`: Wikipedia article title
  - `url`: Direct link to the article
  - `last_modified`: Last modification date
  - `word_count`: Number of words in the article
- **facts**: Array of extracted information
  - `fact`: A specific, atomic piece of information
  - `source_ids`: Array of source IDs supporting this fact
  - `category`: Classification (definition, history, application, technical, other)
- **summary**: Brief overview synthesizing all facts

## Usage Examples

### Command Line Configuration

Edit `config.yaml`:
```yaml
agent:
  output_format: "json"
```

Then use the agent normally:
```bash
wikipedia-agent-cli "What is quantum computing?"
```

### Python API

#### Option 1: Configuration File
```python
# Set output_format: "json" in config.yaml
from src.agent import WikipediaAgent
from src.config import Config

config = Config("config.yaml")
agent = WikipediaAgent(config)
response = agent.query("What is machine learning?")
print(response)  # JSON output
```

#### Option 2: Programmatic Override
```python
from src.agent import WikipediaAgent
from src.config import Config
import json

config = Config("config.yaml")
config._config["agent"]["output_format"] = "json"
agent = WikipediaAgent(config)

response = agent.query("What is artificial intelligence?")
data = json.loads(response)

# Access structured data
print(f"Found {len(data['sources'])} sources")
print(f"Extracted {len(data['facts'])} facts")
for fact in data['facts']:
    print(f"- {fact['fact']} (from {fact['source_ids']})")
```

### Switching Between Modes

```python
from src.agent import WikipediaAgent
from src.config import Config

# MLA mode
config_mla = Config("config.yaml")
config_mla._config["agent"]["output_format"] = "mla"
agent_mla = WikipediaAgent(config_mla)
mla_response = agent_mla.query("What is Python?")

# JSON mode
config_json = Config("config.yaml")
config_json._config["agent"]["output_format"] = "json"
agent_json = WikipediaAgent(config_json)
json_response = agent_json.query("What is Python?")
```

## Use Cases

### MLA Mode
- Academic research papers
- Educational content
- Blog posts and articles
- Any human-readable narrative output
- When proper citations are required

### JSON Mode
- Building knowledge bases
- Data pipelines and automation
- API responses
- Integration with other systems
- Fact extraction and analysis
- Machine learning datasets
- Chatbot knowledge sources

## Testing

Two test/demo scripts are provided:

### 1. Demo Script (`demo_json_mode.py`)
Demonstrates both modes with example queries:
```bash
python demo_json_mode.py
```

### 2. Test Script (`test_json_mode.py`)
Validates JSON structure and both modes:
```bash
python test_json_mode.py
```

## Implementation Details

### Workflow in JSON Mode

1. **Initialization**: When a query starts in JSON mode, `WikipediaAgent` creates a new `FactAccumulator` and registers it globally
2. **Article Retrieval**: `search_and_retrieve_articles_json` tool retrieves Wikipedia articles and automatically registers their metadata as sources
3. **Fact Extraction**: As the LLM reads articles, it calls `record_fact(fact, source_ids, category)` for each insight
4. **Accumulation**: Each call to `record_fact()` stores the fact in the accumulator
5. **JSON Generation**: After the LLM finishes, the agent calls `fact_accumulator.to_json()` to get perfect JSON

### Tool Selection
The agent automatically selects the appropriate tool set based on `output_format`:
- **MLA mode**: Uses `search_and_retrieve_articles` (returns formatted text with MLA citations)
- **JSON mode**: Uses `search_and_retrieve_articles_json` + `record_fact` (tool-based extraction)

### Prompt Engineering
Different system prompts guide the LLM's behavior:
- **MLA prompt**: Emphasizes narrative writing with proper in-text citations
- **JSON prompt**: Instructs LLM to use `record_fact()` tool as it discovers information

### Streaming Support
Both modes support streaming responses. For JSON mode:
- The complete JSON is yielded at the end (since it's generated programmatically)
- Status updates show fact accumulation progress in real-time
- Clients receive the final JSON as a single chunk

## Future Enhancements

Potential improvements enabled by the tool-based approach:
1. **Enhanced Fact Metadata**: Add confidence scores, timestamps, or importance ratings to `record_fact()`
2. **More Categories**: Add statistics, quotes, dates, people, places as fact categories
3. **Quote Extraction**: Add `record_quote()` tool for verbatim quotes with page numbers
4. **Fact Relationships**: Add `link_facts()` tool to connect related facts
5. **Real-time Validation**: Validate facts as they're recorded, not at the end
6. **Fact Suggestions**: LLM could ask for clarification using a `clarify_fact()` tool
7. **Deduplication**: Automatically merge similar facts from different sources
8. **Source Relevance**: Track which sources were most useful via fact counts
9. **LLM-Generated Summary**: Add `generate_summary()` tool call at the end instead of automatic summary

## Migration Notes

Existing code using the agent will continue to work without changes, as MLA mode is the default. To use JSON mode, simply update the configuration or override it programmatically.

No breaking changes were introduced. All existing functionality remains intact.
