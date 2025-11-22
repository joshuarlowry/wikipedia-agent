"""Wikipedia search and article retrieval."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
import wikipediaapi
import requests


@dataclass
class WikipediaArticle:
    """Represents a Wikipedia article."""

    title: str
    url: str
    summary: str
    content: str
    last_modified: Optional[datetime] = None
    word_count: int = 0

    def truncate_content(self, max_chars: int) -> str:
        """Truncate article content to maximum characters."""
        if len(self.content) <= max_chars:
            return self.content
        return self.content[:max_chars] + "..."


class WikipediaSearch:
    """Handles Wikipedia searching and article retrieval."""

    def __init__(self, language: str = "en", user_agent: str = "WikipediaAgent/0.1"):
        """Initialize Wikipedia API client."""
        self.language = language
        self.user_agent = user_agent
        self.wiki = wikipediaapi.Wikipedia(
            language=language,
            user_agent=user_agent,
        )
        self.api_url = f"https://{language}.wikipedia.org/w/api.php"

    def search(self, query: str, max_results: int = 3) -> List[str]:
        """
        Search Wikipedia and return article titles using MediaWiki API.
        """
        try:
            # Use MediaWiki API search endpoint
            params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": max_results,
                "format": "json",
            }

            headers = {"User-Agent": self.user_agent}
            response = requests.get(self.api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            search_results = data.get("query", {}).get("search", [])

            return [result["title"] for result in search_results]
        except Exception as e:
            # Fallback to direct page lookup
            print(f"Search API failed: {e}, trying direct lookup...")
            page = self.wiki.page(query)
            if page.exists():
                return [page.title]
            return []

    def get_article(self, title: str) -> Optional[WikipediaArticle]:
        """Retrieve a Wikipedia article by title."""
        page = self.wiki.page(title)

        if not page.exists():
            return None

        # Get last modified date from API
        last_modified = self._get_last_modified(title)

        return WikipediaArticle(
            title=page.title,
            url=page.fullurl,
            summary=page.summary,
            content=page.text,
            last_modified=last_modified,
            word_count=len(page.text.split()),
        )

    def get_articles(self, titles: List[str]) -> List[WikipediaArticle]:
        """Retrieve multiple Wikipedia articles."""
        articles = []
        for title in titles:
            article = self.get_article(title)
            if article:
                articles.append(article)
        return articles

    def search_and_retrieve(
        self, query: str, max_articles: int = 3, max_chars_per_article: int = 3000
    ) -> List[WikipediaArticle]:
        """Search Wikipedia and retrieve full articles."""
        # Use proper search to find relevant articles
        titles = self.search(query, max_results=max_articles)

        articles = []
        for title in titles:
            page = self.wiki.page(title)
            if page.exists():
                # Get last modified date
                last_modified = self._get_last_modified(title)

                article = WikipediaArticle(
                    title=page.title,
                    url=page.fullurl,
                    summary=page.summary,
                    content=page.text[:max_chars_per_article],
                    last_modified=last_modified,
                    word_count=len(page.text.split()),
                )
                articles.append(article)

        return articles

    def _get_last_modified(self, title: str) -> Optional[datetime]:
        """Get the last modified date of a Wikipedia article."""
        try:
            params = {
                "action": "query",
                "titles": title,
                "prop": "revisions",
                "rvprop": "timestamp",
                "rvlimit": 1,
                "format": "json",
            }
            headers = {"User-Agent": self.user_agent}
            response = requests.get(self.api_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            pages = data.get("query", {}).get("pages", {})

            for page_id, page_data in pages.items():
                if "revisions" in page_data:
                    timestamp_str = page_data["revisions"][0]["timestamp"]
                    # Parse ISO 8601 timestamp (e.g., "2024-11-15T10:30:00Z")
                    return datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

            return None
        except Exception as e:
            print(f"Failed to get last modified date for '{title}': {e}")
            return None
