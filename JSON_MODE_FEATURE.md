# JSON Output Mode Feature

## Overview

The Wikipedia Agent now supports two output formats:

1. **MLA Mode** (default): Returns narrative responses with proper MLA 9th edition citations
2. **JSON Mode** (new): Returns structured data with sources, facts, and references

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
Added a new `system_prompt_json` that instructs the LLM to:
- Extract specific facts from Wikipedia sources
- Link each fact to its source(s)
- Return only valid JSON output
- Categorize facts (definition, history, application, technical, other)

### 3. Wikipedia Tools (`src/wikipedia/tools.py`)
Created new tool `search_and_retrieve_articles_json` that:
- Returns articles in JSON format instead of formatted text
- Provides structured metadata for each source
- Assigns unique IDs to sources for referencing
- Exports separate tool list `wikipedia_tools_json` for JSON mode

### 4. Configuration Manager (`src/config.py`)
Added `output_format` property to access the configured mode

### 5. Agent (`src/agent.py`)
- Detects output format from configuration
- Selects appropriate tools (MLA or JSON) based on mode
- Uses different system prompts for each mode
- Provides mode-specific instructions to the LLM

### 6. Documentation (`README.md`)
Added comprehensive documentation with:
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

### Tool Selection
The agent automatically selects the appropriate tool set based on `output_format`:
- **MLA mode**: Uses `search_and_retrieve_articles` (returns formatted text with MLA citations)
- **JSON mode**: Uses `search_and_retrieve_articles_json` (returns structured JSON)

### Prompt Engineering
Different system prompts guide the LLM's behavior:
- **MLA prompt**: Emphasizes narrative writing with proper in-text citations
- **JSON prompt**: Emphasizes fact extraction and structured data output

### Streaming Support
Both modes support streaming responses. For JSON mode:
- Partial JSON chunks are streamed as the LLM generates them
- Client should accumulate chunks and parse once complete

## Future Enhancements

Potential improvements:
1. Add more fact categories (statistics, quotes, dates, people, places)
2. Include confidence scores for facts
3. Add direct quote extraction with page references
4. Support multiple citation formats (APA, Chicago, etc.)
5. Add validation for JSON schema
6. Include source relevance scoring
7. Add fact deduplication across sources
8. Extract relationships between facts

## Migration Notes

Existing code using the agent will continue to work without changes, as MLA mode is the default. To use JSON mode, simply update the configuration or override it programmatically.

No breaking changes were introduced. All existing functionality remains intact.
