#!/usr/bin/env python3
"""Simple test script for the Strands-powered Wikipedia agent."""

from src.agent import WikipediaAgent
from src.config import Config

def test_agent():
    """Test the Wikipedia agent with a simple query."""
    print("Initializing Wikipedia agent with Strands...")

    try:
        config = Config("config.yaml")
        agent = WikipediaAgent(config)

        print(f"Agent initialized successfully!")
        print(f"Provider: {config.llm_provider}")
        print(f"Model: {config.ollama_config.get('model', 'unknown')}")
        print(f"Ready: {agent.is_ready}")
        print("\n" + "="*80)

        # Test query
        question = "What is quantum computing?"
        print(f"\nQuestion: {question}\n")
        print("Generating response...\n")

        response = agent.query(question, stream=False)
        print(response)

        print("\n" + "="*80)
        print("Test completed successfully!")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_agent()
