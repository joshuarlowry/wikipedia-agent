"""MLA citation generator for Wikipedia articles."""

from datetime import datetime
from typing import List
from .search import WikipediaArticle


class WikipediaCitation:
    """Generates MLA format citations for Wikipedia articles."""

    @staticmethod
    def format_mla(article: WikipediaArticle, access_date: datetime | None = None) -> str:
        """
        Format a Wikipedia article in MLA 9th edition style.

        Format: "Article Title." Wikipedia, Wikimedia Foundation, Last Modified Date,
                URL. Accessed Access Date.

        Example: "Quantum Computing." Wikipedia, Wikimedia Foundation, 15 Nov. 2024,
                 en.wikipedia.org/wiki/Quantum_computing. Accessed 21 Nov. 2025.
        """
        if access_date is None:
            access_date = datetime.now()

        # Format the title
        title = f'"{article.title}."'

        # Format last modified date if available
        modified_str = ""
        if article.last_modified:
            modified_str = f" {WikipediaCitation._format_date(article.last_modified)},"

        # Clean URL (remove https://)
        clean_url = article.url.replace("https://", "").replace("http://", "")

        # Format access date
        access_str = f"Accessed {WikipediaCitation._format_date(access_date)}."

        # Construct MLA citation
        # Note: Wikipedia should be italicized in MLA format
        citation = f"{title} *Wikipedia*, Wikimedia Foundation,{modified_str} {clean_url}. {access_str}"

        return citation

    @staticmethod
    def format_multiple_mla(
        articles: List[WikipediaArticle], access_date: datetime | None = None
    ) -> List[str]:
        """Generate MLA citations for multiple articles."""
        if access_date is None:
            access_date = datetime.now()

        return [WikipediaCitation.format_mla(article, access_date) for article in articles]

    @staticmethod
    def format_works_cited(
        articles: List[WikipediaArticle], access_date: datetime | None = None
    ) -> str:
        """Generate a complete Works Cited section."""
        citations = WikipediaCitation.format_multiple_mla(articles, access_date)
        return "\n".join(citations)

    @staticmethod
    def _format_date(date: datetime) -> str:
        """Format date in MLA style (e.g., '21 Nov. 2025')."""
        month_abbrev = {
            1: "Jan.",
            2: "Feb.",
            3: "Mar.",
            4: "Apr.",
            5: "May",
            6: "June",
            7: "July",
            8: "Aug.",
            9: "Sept.",
            10: "Oct.",
            11: "Nov.",
            12: "Dec.",
        }

        day = date.day
        month = month_abbrev[date.month]
        year = date.year

        return f"{day} {month} {year}"
