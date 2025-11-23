#!/usr/bin/env python
"""Simple test to verify Wikipedia search and agent work."""

from src.config import Config
from src.agent import WikipediaAgent
from src.wikipedia.search import WikipediaSearch

print("Testing Wikipedia Research Agent")
print("=" * 50)
print()

# Initialize
config = Config("config.yaml")
agent = WikipediaAgent(config)

print(f"✓ Agent initialized")
print(f"  Provider: {config.llm_provider}")
print(f"  Model: {config.ollama_config.get('model')}")
print(f"  Agent ready: {agent.is_ready}")
print()

# Test Wikipedia search directly (tools use this internally)
print("Testing Wikipedia search (via WikipediaSearch)...")
try:
    search = WikipediaSearch(language="en", user_agent="WikipediaAgent/0.1")
    articles = search.search_and_retrieve("Python programming", max_articles=3)
    if articles:
        print(f"✓ Found {len(articles)} article(s):")
        for article in articles:
            print(f"  - {article.title}")
            print(f"    URL: {article.url}")
            print(f"    Word count: {article.word_count}")
    else:
        print("✗ No articles found")
except Exception as e:
    print(f"✗ Error during search: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 50)
print("If the search worked, you can now run: ./start.sh")
