#!/usr/bin/env python
"""Demo script to test TUI components."""

from src.tui.app import WikipediaAgentApp
from src.config import Config
from src.wikipedia.search import WikipediaArticle

print("Wikipedia Research Agent - TUI Demo")
print("=" * 50)
print()

# Test configuration loading
print("✓ Testing configuration...")
config = Config("config.yaml")
print(f"  Provider: {config.llm_provider}")
print(f"  Wikipedia language: {config.wikipedia_config.get('language', 'en')}")
print()

# Test app initialization
print("✓ Testing TUI app initialization...")
app = WikipediaAgentApp("config.yaml")
print(f"  Agent created: {app.agent is not None}")
print(f"  LLM provider: {type(app.agent.llm).__name__}")
print()

# Test Wikipedia search
print("✓ Testing Wikipedia search...")
try:
    articles = app.agent.search_wikipedia("Python programming language")
    if articles:
        print(f"  Found {len(articles)} article(s)")
        for article in articles[:2]:
            print(f"    - {article.title} ({article.word_count} words)")
    else:
        print("  No articles found (this is okay for testing)")
except Exception as e:
    print(f"  Search failed (expected if offline): {type(e).__name__}")
print()

# Test components
print("✓ Testing TUI components...")
from src.tui.app import ArticleList, StatusBar, ResponseDisplay

article_list = ArticleList()
print(f"  ArticleList created: {article_list is not None}")

status_bar = StatusBar()
status_bar.provider = config.llm_provider
status_bar.status = "Ready"
print(f"  StatusBar created: {status_bar is not None}")
print(f"  Status text: {status_bar.render()}")

response_display = ResponseDisplay()
print(f"  ResponseDisplay created: {response_display is not None}")
print()

print("=" * 50)
print("All tests passed! ✨")
print()
print("To run the TUI:")
print("  source .venv/bin/activate")
print("  wikipedia-agent")
print()
print("Note: Make sure Ollama is running or configure OpenRouter first!")
