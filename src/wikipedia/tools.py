"""Strands tools for Wikipedia search and citation."""

import json
from datetime import datetime
from typing import List
from strands import tool
from .search import WikipediaSearch, WikipediaArticle
from .citation import WikipediaCitation


# Initialize Wikipedia search instance
_wiki_search = WikipediaSearch(language="en", user_agent="WikipediaAgent/0.1-Strands")


@tool
def search_wikipedia(query: str, max_articles: int = 3) -> str:
    """
    Search Wikipedia for articles related to the query.

    Args:
        query: The search query
        max_articles: Maximum number of articles to return (default: 3)

    Returns:
        A formatted string with article titles and URLs found
    """
    titles = _wiki_search.search(query, max_results=max_articles)

    if not titles:
        return f"No Wikipedia articles found for query: {query}"

    result = f"Found {len(titles)} Wikipedia articles:\n"
    for i, title in enumerate(titles, 1):
        # Get basic article info
        article = _wiki_search.get_article(title)
        if article:
            result += f"\n{i}. {article.title}\n   URL: {article.url}\n   Words: {article.word_count}\n"

    return result


@tool
def get_wikipedia_article(title: str, max_chars: int = 3000) -> str:
    """
    Retrieve a specific Wikipedia article by title.

    Args:
        title: The exact title of the Wikipedia article
        max_chars: Maximum characters of content to return (default: 3000)

    Returns:
        The article content with metadata, or an error message if not found
    """
    article = _wiki_search.get_article(title)

    if not article:
        return f"Article '{title}' not found on Wikipedia."

    # Truncate content
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
    """
    Search Wikipedia and retrieve full content of relevant articles.

    This is the main tool for Wikipedia research - it searches for articles
    and returns their full content along with MLA citations.

    Args:
        query: The search query
        max_articles: Maximum number of articles to retrieve (default: 3)
        max_chars_per_article: Maximum characters per article (default: 3000)

    Returns:
        Formatted string with articles and their MLA citations
    """
    articles = _wiki_search.search_and_retrieve(
        query=query,
        max_articles=max_articles,
        max_chars_per_article=max_chars_per_article
    )

    if not articles:
        return f"No Wikipedia articles found for query: {query}"

    # Format articles
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

    # Add MLA citations
    citations = WikipediaCitation.format_multiple_mla(articles, access_date=datetime.now())
    result += f"\n{'='*80}\n"
    result += "Works Cited (MLA Format):\n"
    result += f"{'='*80}\n"
    for citation in citations:
        result += f"{citation}\n\n"

    return result


@tool
def format_mla_citation(title: str) -> str:
    """
    Generate an MLA 9th edition citation for a Wikipedia article.

    Args:
        title: The title of the Wikipedia article

    Returns:
        MLA formatted citation string
    """
    article = _wiki_search.get_article(title)

    if not article:
        return f"Article '{title}' not found on Wikipedia. Cannot generate citation."

    citation = WikipediaCitation.format_mla(article, access_date=datetime.now())
    return citation


@tool
def search_and_retrieve_articles_json(query: str, max_articles: int = 3, max_chars_per_article: int = 3000) -> str:
    """
    Search Wikipedia and retrieve articles in JSON format with structured metadata.

    This tool is designed for JSON output mode - it returns structured data
    about sources that can be used for fact extraction and referencing.

    Args:
        query: The search query
        max_articles: Maximum number of articles to retrieve (default: 3)
        max_chars_per_article: Maximum characters per article (default: 3000)

    Returns:
        JSON string with articles and their metadata
    """
    articles = _wiki_search.search_and_retrieve(
        query=query,
        max_articles=max_articles,
        max_chars_per_article=max_chars_per_article
    )

    if not articles:
        return json.dumps({
            "error": f"No Wikipedia articles found for query: {query}",
            "query": query,
            "sources": [],
            "articles_content": []
        }, indent=2)

    # Format articles as structured JSON
    sources = []
    articles_content = []
    
    for i, article in enumerate(articles, 1):
        source_id = f"source_{i}"
        
        # Source metadata
        sources.append({
            "id": source_id,
            "title": article.title,
            "url": article.url,
            "last_modified": article.last_modified.strftime('%Y-%m-%d') if article.last_modified else None,
            "word_count": article.word_count
        })
        
        # Article content for fact extraction
        articles_content.append({
            "source_id": source_id,
            "title": article.title,
            "summary": article.summary,
            "content": article.content
        })

    result = {
        "query": query,
        "sources": sources,
        "articles_content": articles_content,
        "retrieved_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return json.dumps(result, indent=2)


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
