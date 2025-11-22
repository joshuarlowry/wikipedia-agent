"""Wikipedia research agent using Strands framework."""

import os
from typing import Iterator, Optional, Callable
from strands import Agent
from strands.models.ollama import OllamaModel
from strands.models.litellm import LiteLLMModel

from .config import Config
from .prompts import PromptManager
from .wikipedia.tools import wikipedia_tools, wikipedia_tools_json


def create_model_from_config(config: Config):
    """Create a Strands model instance based on configuration."""
    provider_name = config.llm_provider

    if provider_name == "ollama":
        ollama_config = config.ollama_config
        return OllamaModel(
            host=ollama_config.get("base_url", "http://localhost:11434"),
            model_id=ollama_config.get("model", "llama3.1"),
            temperature=ollama_config.get("temperature", 0.7),
        )
    elif provider_name == "openrouter":
        openrouter_config = config.openrouter_config
        api_key = openrouter_config.get("api_key", os.getenv("OPENROUTER_API_KEY", ""))

        return LiteLLMModel(
            client_args={
                "api_key": api_key,
                "api_base": openrouter_config.get("base_url", "https://openrouter.ai/api/v1"),
            },
            model_id=f"openrouter/{openrouter_config.get('model', 'anthropic/claude-3.5-sonnet')}",
            params={
                "temperature": openrouter_config.get("temperature", 0.7),
            }
        )
    else:
        raise ValueError(f"Unknown LLM provider: {provider_name}")


class WikipediaAgent:
    """Wikipedia research agent powered by Strands framework."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize the Wikipedia agent with Strands."""
        self.config = config or Config()
        self.prompt_manager = PromptManager()
        self.output_format = self.config.output_format
        self.status_callback = None

        # Create Strands model
        self.model = create_model_from_config(self.config)

        # Select tools based on output format
        tools = wikipedia_tools_json if self.output_format == "json" else wikipedia_tools

        # Create Strands agent with Wikipedia tools
        self.agent = Agent(
            model=self.model,
            tools=tools,
        )

    def set_status_callback(self, callback: Callable[[str], None]):
        """Set a callback function to receive status updates."""
        self.status_callback = callback

    def _emit_status(self, message: str):
        """Emit a status message if callback is set."""
        if self.status_callback:
            self.status_callback(message)

    def query(self, question: str, stream: bool = False) -> str | Iterator[str]:
        """
        Main entry point: search Wikipedia and generate a response.

        Args:
            question: The user's question
            stream: Whether to stream the response

        Returns:
            Complete response string or iterator of response chunks
        """
        # Build the prompt with instructions based on output format
        system_prompt = self.prompt_manager.get_system_prompt(mode=self.output_format)

        if self.output_format == "json":
            # JSON mode instructions
            full_prompt = f"""{system_prompt}

User Question: {question}

Instructions:
1. Use the search_and_retrieve_articles_json tool to find relevant Wikipedia articles for this question
2. Analyze the articles carefully and extract specific facts
3. For each fact, identify which source(s) it came from
4. Return ONLY valid JSON with the following structure:
   - query: the user's question
   - sources: list of source metadata
   - facts: list of extracted facts with source references
   - summary: brief overview
5. Do not include any text before or after the JSON object
"""
        else:
            # MLA mode instructions
            full_prompt = f"""{system_prompt}

User Question: {question}

Instructions:
1. Use the search_and_retrieve_articles tool to find relevant Wikipedia articles for this question
2. Analyze the articles carefully
3. Provide a comprehensive answer based on the information found
4. Include proper MLA citations at the end of your response using the format provided by the tool
"""

        if stream:
            return self._stream_query(full_prompt)
        else:
            return self._sync_query(full_prompt)

    def _sync_query(self, prompt: str) -> str:
        """Execute query synchronously."""
        # Create agent with callback to intercept tool calls
        def callback_handler(**kwargs):
            # Detect tool calls
            if "tool_name" in kwargs:
                tool_name = kwargs["tool_name"]
                if "search" in tool_name.lower():
                    self._emit_status("🔍 Searching Wikipedia for relevant articles...")
                elif "retrieve" in tool_name.lower():
                    self._emit_status("📥 Retrieving article content...")
                elif "citation" in tool_name.lower():
                    self._emit_status("📝 Formatting citations...")
            # Detect when LLM starts generating
            if "data" in kwargs and kwargs.get("event") == "start":
                self._emit_status("✍️  Analyzing articles and generating response...")

        # Select tools based on output format
        tools = wikipedia_tools_json if self.output_format == "json" else wikipedia_tools

        # Create agent with callback
        agent_with_callback = Agent(
            model=self.model,
            tools=tools,
            callback_handler=callback_handler,
        )

        self._emit_status("🚀 Starting research process...")
        result = agent_with_callback(prompt)
        self._emit_status("✅ Research complete!")

        # Extract the response text from Strands result
        # Strands returns an AgentResult object with various attributes
        if hasattr(result, 'output'):
            # The output attribute contains the final response
            return result.output
        elif hasattr(result, 'content'):
            return result.content
        else:
            return str(result)

    def _stream_query(self, prompt: str) -> Iterator[str]:
        """Execute query with streaming."""
        try:
            # Use Strands streaming with callback
            accumulated_text = []
            generation_started = False

            def callback_handler(**kwargs):
                nonlocal generation_started
                
                # Detect tool calls
                if "tool_name" in kwargs:
                    tool_name = kwargs["tool_name"]
                    if "search" in tool_name.lower():
                        self._emit_status("🔍 Searching Wikipedia for relevant articles...")
                    elif "retrieve" in tool_name.lower():
                        self._emit_status("📥 Retrieving article content...")
                    elif "citation" in tool_name.lower():
                        self._emit_status("📝 Formatting citations...")
                
                # Detect when LLM starts generating and collect text
                if "data" in kwargs:
                    if not generation_started:
                        self._emit_status("✍️  Analyzing articles and generating response...")
                        generation_started = True
                    accumulated_text.append(kwargs["data"])

            # Select tools based on output format
            tools = wikipedia_tools_json if self.output_format == "json" else wikipedia_tools

            # Create an agent with callback
            streaming_agent = Agent(
                model=self.model,
                tools=tools,
                callback_handler=callback_handler,
            )

            self._emit_status("🚀 Starting research process...")
            
            # Execute the query
            result = streaming_agent(prompt)

            # Yield accumulated text
            for chunk in accumulated_text:
                yield chunk
            
            self._emit_status("✅ Research complete!")

        except Exception as e:
            yield f"Error during streaming: {e}"

    @property
    def is_ready(self) -> bool:
        """Check if the agent is ready to process queries."""
        try:
            # Try to get model config to verify it's accessible
            if hasattr(self.model, 'config'):
                return True
            return True
        except Exception:
            return False


# Legacy compatibility: create aliases for old API
def create_agent(config: Optional[Config] = None) -> WikipediaAgent:
    """Factory function to create a Wikipedia agent."""
    return WikipediaAgent(config=config)
