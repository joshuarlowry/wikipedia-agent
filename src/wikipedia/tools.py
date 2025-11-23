"""Strands tools for Wikipedia search and citation."""

import json
from datetime import datetime
from typing import List, Optional
from strands import tool
from .search import WikipediaSearch, WikipediaArticle
from .citation import WikipediaCitation


# Initialize Wikipedia search instance
_wiki_search = WikipediaSearch(language="en", user_agent="WikipediaAgent/0.1-Strands")

# Global fact accumulator (will be set by agent)
_fact_accumulator = None


def set_fact_accumulator(accumulator):
    """Set the global fact accumulator for JSON mode."""
    global _fact_accumulator
    _fact_accumulator = accumulator


def get_fact_accumulator():
    """Get the global fact accumulator."""
    return _fact_accumulator


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
    Search Wikipedia and retrieve articles for fact extraction.

    This tool searches Wikipedia, retrieves article content, and automatically
    registers the sources with the fact accumulator. After calling this tool,
    use record_fact() to extract specific information from the articles.

    Args:
        query: The search query
        max_articles: Maximum number of articles to retrieve (default: 3)
        max_chars_per_article: Maximum characters per article (default: 3000)

    Returns:
        Formatted string with article content and source IDs for fact extraction
    """
    articles = _wiki_search.search_and_retrieve(
        query=query,
        max_articles=max_articles,
        max_chars_per_article=max_chars_per_article
    )

    if not articles:
        return f"No Wikipedia articles found for query: {query}"

    # Register sources with fact accumulator
    accumulator = get_fact_accumulator()
    
    result = f"Retrieved {len(articles)} Wikipedia articles:\n\n"
    
    for i, article in enumerate(articles, 1):
        source_id = f"source_{i}"
        
        # Register source with accumulator
        if accumulator:
            accumulator.add_source(
                source_id=source_id,
                title=article.title,
                url=article.url,
                last_modified=article.last_modified.strftime('%Y-%m-%d') if article.last_modified else "Unknown",
                word_count=article.word_count
            )
        
        # Format article for LLM to read
        result += f"{'='*80}\n"
        result += f"SOURCE ID: {source_id}\n"
        result += f"Article: {article.title}\n"
        result += f"{'='*80}\n"
        result += f"URL: {article.url}\n"
        result += f"Word Count: {article.word_count}\n"
        result += f"Last Modified: {article.last_modified.strftime('%Y-%m-%d') if article.last_modified else 'Unknown'}\n\n"
        result += f"Summary:\n{article.summary}\n\n"
        result += f"Content:\n{article.content}\n\n"
    
    result += "\nIMPORTANT: As you read through these articles, use the record_fact() tool to save "
    result += "important information. Reference the SOURCE ID for each fact you extract.\n"
    
    return result


@tool
def record_fact(fact: str, source_ids: List[str], category: str) -> str:
    """
    Record a fact or insight discovered from Wikipedia articles.
    
    Call this tool each time you discover an important piece of information
    while reading the articles. The system will accumulate all facts and
    generate structured JSON output at the end.
    
    Args:
        fact: A clear, specific piece of information (be precise and factual)
        source_ids: List of source IDs that support this fact (e.g., ["source_1", "source_2"])
        category: Category of the fact - must be one of:
                  - "definition": Core definitions and explanations
                  - "history": Historical information, timeline, origins
                  - "application": Practical uses, real-world applications
                  - "technical": Technical details, specifications, mechanisms
                  - "other": Any other relevant information
    
    Returns:
        Confirmation message indicating the fact was recorded
    
    Example usage:
        record_fact(
            fact="Quantum computing uses quantum bits (qubits) that can exist in superposition.",
            source_ids=["source_1"],
            category="definition"
        )
    """
    accumulator = get_fact_accumulator()
    
    if not accumulator:
        return "Error: Fact accumulator not initialized"
    
    return accumulator.record_fact(fact, source_ids, category)


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
    record_fact,
]
