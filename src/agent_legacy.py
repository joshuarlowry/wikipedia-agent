"""Core Wikipedia research agent."""

from datetime import datetime
from typing import Iterator, List, Optional
from .config import Config
from .prompts import PromptManager
from .wikipedia import WikipediaSearch, WikipediaCitation
from .wikipedia.search import WikipediaArticle
from .llm import LLMProvider, OllamaProvider, OpenRouterProvider


class WikipediaAgent:
    """Main agent that coordinates Wikipedia search and LLM response generation."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the Wikipedia agent."""
        self.config = config or Config()

        # Initialize components
        self.prompt_manager = PromptManager()
        self.wikipedia = WikipediaSearch(
            language=self.config.wikipedia_config.get("language", "en")
        )

        # Initialize LLM provider
        self.llm = self._create_llm_provider()

    def _create_llm_provider(self) -> LLMProvider:
        """Create the appropriate LLM provider based on configuration."""
        provider_name = self.config.llm_provider

        if provider_name == "ollama":
            config = self.config.ollama_config
            return OllamaProvider(
                model=config.get("model", "llama3.2"),
                base_url=config.get("base_url", "http://localhost:11434"),
                temperature=config.get("temperature", 0.7),
            )
        elif provider_name == "openrouter":
            config = self.config.openrouter_config
            return OpenRouterProvider(
                model=config.get("model", "anthropic/claude-3.5-sonnet"),
                api_key=config.get("api_key", ""),
                base_url=config.get("base_url", "https://openrouter.ai/api/v1"),
                temperature=config.get("temperature", 0.7),
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider_name}")

    def search_wikipedia(self, query: str) -> List[WikipediaArticle]:
        """Search Wikipedia and retrieve articles."""
        max_articles = self.config.wikipedia_config.get("max_articles", 3)
        max_chars = self.config.wikipedia_config.get("max_chars_per_article", 3000)

        articles = self.wikipedia.search_and_retrieve(
            query=query, max_articles=max_articles, max_chars_per_article=max_chars
        )

        return articles

    def generate_response(self, question: str, articles: List[WikipediaArticle]) -> str:
        """Generate a response using the LLM with retrieved articles."""
        # Format sources
        sources_text = self._format_sources(articles)

        # Generate citations
        citations = WikipediaCitation.format_multiple_mla(
            articles, access_date=datetime.now()
        )
        citations_text = "\n".join(citations)

        # Get prompts
        system_prompt = self.prompt_manager.get_system_prompt()
        user_prompt = self.prompt_manager.format_user_prompt(
            question=question, sources=sources_text, citations=citations_text
        )

        # Generate response
        response = self.llm.generate(system_prompt, user_prompt)
        return response.content

    def stream_response(
        self, question: str, articles: List[WikipediaArticle]
    ) -> Iterator[str]:
        """Generate a streaming response using the LLM."""
        # Format sources
        sources_text = self._format_sources(articles)

        # Generate citations
        citations = WikipediaCitation.format_multiple_mla(
            articles, access_date=datetime.now()
        )
        citations_text = "\n".join(citations)

        # Get prompts
        system_prompt = self.prompt_manager.get_system_prompt()
        user_prompt = self.prompt_manager.format_user_prompt(
            question=question, sources=sources_text, citations=citations_text
        )

        # Stream response
        yield from self.llm.stream_generate(system_prompt, user_prompt)

    def query(self, question: str, stream: bool = False) -> str | Iterator[str]:
        """
        Main entry point: search Wikipedia and generate a response.

        Args:
            question: The user's question
            stream: Whether to stream the response

        Returns:
            Complete response string or iterator of response chunks
        """
        # Search Wikipedia
        articles = self.search_wikipedia(question)

        if not articles:
            error_msg = "No Wikipedia articles found for the query."
            return iter([error_msg]) if stream else error_msg

        # Generate response
        if stream:
            return self.stream_response(question, articles)
        else:
            return self.generate_response(question, articles)

    def _format_sources(self, articles: List[WikipediaArticle]) -> str:
        """Format articles as source text for the LLM."""
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append(f"Source {i}: {article.title}")
            formatted.append(f"URL: {article.url}")
            formatted.append(f"Content:\n{article.content}\n")

        return "\n".join(formatted)

    @property
    def is_ready(self) -> bool:
        """Check if the agent is ready to process queries."""
        return self.llm.is_available
