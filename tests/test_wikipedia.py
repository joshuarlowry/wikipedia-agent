"""Tests for Wikipedia search and citation functionality."""

import pytest
from datetime import datetime
from src.wikipedia import WikipediaSearch, WikipediaCitation
from src.wikipedia.search import WikipediaArticle


class TestWikipediaSearch:
    """Tests for WikipediaSearch class."""

    def test_init(self):
        """Test WikipediaSearch initialization."""
        search = WikipediaSearch(language="en")
        assert search.language == "en"
        assert search.wiki is not None

    def test_get_article_existing(self):
        """Test retrieving an existing Wikipedia article."""
        search = WikipediaSearch()
        article = search.get_article("Python (programming language)")

        assert article is not None
        assert article.title is not None
        assert article.url is not None
        assert article.content is not None
        assert len(article.content) > 0

    def test_get_article_nonexistent(self):
        """Test retrieving a non-existent article."""
        search = WikipediaSearch()
        article = search.get_article("ThisArticleDefinitelyDoesNotExist12345")

        assert article is None

    def test_search_and_retrieve(self):
        """Test searching and retrieving articles."""
        search = WikipediaSearch()
        articles = search.search_and_retrieve("Python (programming language)", max_articles=1)

        assert len(articles) > 0
        assert articles[0].title is not None
        assert articles[0].url is not None

    def test_truncate_content(self):
        """Test content truncation."""
        article = WikipediaArticle(
            title="Test",
            url="https://test.com",
            summary="Summary",
            content="A" * 1000,
            word_count=1000,
        )

        truncated = article.truncate_content(100)
        assert len(truncated) <= 103  # 100 + "..."
        assert truncated.endswith("...")


class TestWikipediaCitation:
    """Tests for WikipediaCitation class."""

    def test_format_date(self):
        """Test MLA date formatting."""
        date = datetime(2025, 11, 21)
        formatted = WikipediaCitation._format_date(date)
        assert formatted == "21 Nov. 2025"

    def test_format_date_may(self):
        """Test May formatting (no period)."""
        date = datetime(2024, 5, 15)
        formatted = WikipediaCitation._format_date(date)
        assert formatted == "15 May 2024"

    def test_format_mla(self):
        """Test MLA citation formatting."""
        article = WikipediaArticle(
            title="Quantum Computing",
            url="https://en.wikipedia.org/wiki/Quantum_computing",
            summary="Summary",
            content="Content",
        )

        access_date = datetime(2025, 11, 21)
        citation = WikipediaCitation.format_mla(article, access_date)

        assert '"Quantum Computing."' in citation
        assert "Wikipedia" in citation
        assert "Wikimedia Foundation" in citation
        assert "en.wikipedia.org/wiki/Quantum_computing" in citation
        assert "Accessed 21 Nov. 2025." in citation

    def test_format_multiple_mla(self):
        """Test formatting multiple citations."""
        articles = [
            WikipediaArticle(
                title="Article 1",
                url="https://en.wikipedia.org/wiki/Article_1",
                summary="Summary 1",
                content="Content 1",
            ),
            WikipediaArticle(
                title="Article 2",
                url="https://en.wikipedia.org/wiki/Article_2",
                summary="Summary 2",
                content="Content 2",
            ),
        ]

        citations = WikipediaCitation.format_multiple_mla(articles)
        assert len(citations) == 2
        assert '"Article 1."' in citations[0]
        assert '"Article 2."' in citations[1]

    def test_format_works_cited(self):
        """Test Works Cited section formatting."""
        articles = [
            WikipediaArticle(
                title="Test Article",
                url="https://en.wikipedia.org/wiki/Test",
                summary="Summary",
                content="Content",
            )
        ]

        works_cited = WikipediaCitation.format_works_cited(articles)
        assert '"Test Article."' in works_cited
        assert "Wikipedia" in works_cited
