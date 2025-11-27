"""Strands tools for Wikipedia search and citation."""

from datetime import datetime
from strands import tool
from .search import WikipediaSearch, WikipediaArticle
from .citation import WikipediaCitation


# Initialize Wikipedia search instance
_wiki_search = WikipediaSearch(language="en", user_agent="WikipediaAgent/0.1-Strands")


@tool
def search_wikipedia(query: str, max_articles: int = 3) -> str:
    """Search Wikipedia for articles related to the query."""
    titles = _wiki_search.search(query, max_results=max_articles)

    if not titles:
        return f"No Wikipedia articles found for query: {query}"

    result = f"Found {len(titles)} Wikipedia articles:\n"
    for i, title in enumerate(titles, 1):
        article = _wiki_search.get_article(title)
        if article:
            result += f"\n{i}. {article.title}\n   URL: {article.url}\n   Words: {article.word_count}\n"

    return result


@tool
def get_wikipedia_article(title: str, max_chars: int = 3000) -> str:
    """Retrieve a specific Wikipedia article by title."""
    article = _wiki_search.get_article(title)

    if not article:
        return f"Article '{title}' not found on Wikipedia."

    content = article.content[:max_chars]
    if len(article.content) > max_chars:
        content += "..."

    result = f"""Title: {article.title}
URL: {article.url}
Last Modified: {article.last_modified.strftime('%Y-%m-%d') if article.last_modified else 'Unknown'}
Word Count: {article.word_count}

Summary:
{article.summary}

Content:
{content}
"""

    return result


@tool
def search_and_retrieve_articles(query: str, max_articles: int = 3, max_chars_per_article: int = 3000) -> str:
    """Search Wikipedia and retrieve full content of relevant articles."""
    articles = _wiki_search.search_and_retrieve(
        query=query,
        max_articles=max_articles,
        max_chars_per_article=max_chars_per_article
    )

    if not articles:
        return f"No Wikipedia articles found for query: {query}"

    result = f"Retrieved {len(articles)} Wikipedia articles:\n\n"

    for i, article in enumerate(articles, 1):
        result += f"{'='*80}\n"
        result += f"Article {i}: {article.title}\n"
        result += f"{'='*80}\n"
        result += f"URL: {article.url}\n"
        result += f"Word Count: {article.word_count}\n"
        result += f"Last Modified: {article.last_modified.strftime('%Y-%m-%d') if article.last_modified else 'Unknown'}\n\n"
        result += f"Summary:\n{article.summary}\n\n"
        result += f"Content:\n{article.content}\n\n"

    citations = WikipediaCitation.format_multiple_mla(articles, access_date=datetime.now())
    result += f"\n{'='*80}\n"
    result += "Works Cited (MLA Format):\n"
    result += f"{'='*80}\n"
    for citation in citations:
        result += f"{citation}\n\n"

    return result


@tool
def format_mla_citation(title: str) -> str:
    """Generate an MLA 9th edition citation for a Wikipedia article."""
    article = _wiki_search.get_article(title)

    if not article:
        return f"Article '{title}' not found on Wikipedia. Cannot generate citation."

    citation = WikipediaCitation.format_mla(article, access_date=datetime.now())
    return citation


@tool
def search_and_retrieve_articles_json(query: str, max_articles: int = 3, max_chars_per_article: int = 3000) -> str:
    """Search Wikipedia and retrieve articles for JSON extraction."""
    articles = _wiki_search.search_and_retrieve(
        query=query,
        max_articles=max_articles,
        max_chars_per_article=max_chars_per_article
    )

    if not articles:
        return f"No Wikipedia articles found for query: {query}"

    result = f"Retrieved {len(articles)} Wikipedia articles:\n\n"

    for i, article in enumerate(articles, 1):
        source_id = f"source_{i}"
        result += f"{'='*80}\n"
        result += f"SOURCE ID: {source_id}\n"
        result += f"Article: {article.title}\n"
        result += f"{'='*80}\n"
        result += f"URL: {article.url}\n"
        result += f"Word Count: {article.word_count}\n"
        result += f"Last Modified: {article.last_modified.strftime('%Y-%m-%d') if article.last_modified else 'Unknown'}\n\n"
        result += f"Summary:\n{article.summary}\n\n"
        result += f"Content:\n{article.content}\n\n"

    result += "\nIMPORTANT: Use the provided SOURCE IDs when referencing facts in JSON.\n"

    return result


# Export tools list for easy registration
wikipedia_tools = [
    search_wikipedia,
    get_wikipedia_article,
    search_and_retrieve_articles,
    format_mla_citation,
]

# Separate tool list for JSON mode
wikipedia_tools_json = [
    search_wikipedia,
    get_wikipedia_article,
    search_and_retrieve_articles_json,
]
