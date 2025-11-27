"""Wikipedia research agent using Strands framework."""

import json
import os
from typing import Iterator, Optional, Callable, Union

from strands import Agent
from strands.models.litellm import LiteLLMModel
from strands.models.ollama import OllamaModel
from strands.types.exceptions import StructuredOutputException

from .config import Config
from .fact_accumulator import FactAccumulator
from .fact_models import FactOutput
from .prompts import PromptManager
from .wikipedia.tools import (
    set_fact_accumulator,
    wikipedia_tools,
    wikipedia_tools_json,
)


def create_model_from_config(config: Config):
    """Create a Strands model instance based on configuration."""
    provider_name = config.llm_provider

    if provider_name == "ollama":
        ollama_config = config.ollama_config
        return OllamaModel(
            host=ollama_config.get("base_url", "http://masterroshi:11434"),
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
        self.fact_accumulator = None

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

    def query(self, question: str, stream: bool = False) -> Union[str, Iterator[str]]:
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
            # Initialize fact accumulator for JSON mode
            self.fact_accumulator = FactAccumulator(query=question)
            set_fact_accumulator(self.fact_accumulator)
            
            # JSON mode instructions
            full_prompt = f"""{system_prompt}

User Question: {question}

Instructions:
1. Use the search_and_retrieve_articles_json tool to find relevant Wikipedia articles for this question
2. Read through the articles carefully
3. As you discover important information, use the record_fact() tool to save each fact
4. For each fact, specify:
   - The fact itself (be specific and precise)
   - The source_ids that support it (provided in the article headers)
   - The category (definition, history, application, technical, or other)
5. Extract as many relevant facts as you can find
6. When you're done extracting facts, simply indicate you've finished

Remember: Use record_fact() for EACH piece of information you want to save.
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
        # Track fact recording for status updates
        fact_count = [0]  # Use list to allow modification in closure
        
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
                elif "record_fact" in tool_name.lower():
                    fact_count[0] += 1
                    self._emit_status(f"💾 Recording facts... ({fact_count[0]} recorded)")
            # Detect when LLM starts generating
            if "data" in kwargs and kwargs.get("event") == "start":
                if self.output_format == "json":
                    self._emit_status("✍️  Reading articles and extracting facts...")
                else:
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

        # For JSON mode, request structured output matching FactOutput
        if self.output_format == "json":
            try:
                result = agent_with_callback(
                    prompt,
                    structured_output_model=FactOutput,
                )
                self._emit_status("✅ Research complete!")

                # Return JSON string to preserve existing public contract
                if result.structured_output is not None:
                    return json.dumps(result.structured_output.model_dump(), indent=2)

                # Fallback: if for some reason no structured_output, fall back to accumulator
                if self.fact_accumulator:
                    return self.fact_accumulator.to_json()

                # Final fallback: stringify raw result
                if hasattr(result, "output"):
                    return str(result.output)
                return str(result)
            except StructuredOutputException as exc:
                # Surface a clear error while keeping response JSON-serializable
                self._emit_status("⚠️ Failed to validate structured JSON output.")
                error_payload = {
                    "query": question,
                    "sources": [],
                    "facts": [],
                    "summary": (
                        "Failed to produce structured JSON output: "
                        f"{getattr(exc, 'message', str(exc))}"
                    ),
                }
                return json.dumps(error_payload, indent=2)

        # Non-JSON (MLA) mode: standard Strands text behavior
        result = agent_with_callback(prompt)
        self._emit_status("✅ Research complete!")

        # Strands returns an AgentResult object with various attributes
        if hasattr(result, "output"):
            # The output attribute contains the final response
            return result.output
        if hasattr(result, "content"):
            return result.content
        return str(result)

    def _stream_query(self, prompt: str) -> Iterator[str]:
        """Execute query with streaming."""
        try:
            # Use Strands streaming with callback
            accumulated_text = []
            generation_started = False
            fact_count = [0]  # Use list to allow modification in closure

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
                    elif "record_fact" in tool_name.lower():
                        fact_count[0] += 1
                        self._emit_status(f"💾 Recording facts... ({fact_count[0]} recorded)")
                
                # Detect when LLM starts generating and collect text
                if "data" in kwargs:
                    if not generation_started:
                        if self.output_format == "json":
                            self._emit_status("✍️  Reading articles and extracting facts...")
                        else:
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

            if self.output_format == "json":
                # In JSON mode we don't truly stream structured output yet;
                # yield the final JSON document once it's ready.
                try:
                    structured_result = streaming_agent(
                        prompt,
                        structured_output_model=FactOutput,
                    )
                    if structured_result.structured_output is not None:
                        json_output = json.dumps(
                            structured_result.structured_output.model_dump(),
                            indent=2,
                        )
                        yield json_output
                    else:
                        # Fallback to accumulator-based JSON if available
                        if self.fact_accumulator:
                            yield self.fact_accumulator.to_json()
                        else:
                            yield str(result)
                except StructuredOutputException as exc:
                    self._emit_status("⚠️ Failed to validate structured JSON output.")
                    error_payload = {
                        "query": prompt,
                        "sources": [],
                        "facts": [],
                        "summary": (
                            "Failed to produce structured JSON output: "
                            f"{getattr(exc, 'message', str(exc))}"
                        ),
                    }
                    yield json.dumps(error_payload, indent=2)
            else:
                # For MLA mode, yield accumulated text if we got any
                if accumulated_text:
                    for chunk in accumulated_text:
                        yield chunk
                else:
                    # Fallback: if streaming didn't capture chunks, use the result directly
                    if hasattr(result, "output"):
                        yield result.output
                    elif hasattr(result, "content"):
                        yield result.content
                    else:
                        yield str(result)

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
