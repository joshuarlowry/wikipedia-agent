#!/usr/bin/env python3
"""Demo script showing both MLA and JSON output modes."""

import json
from src.agent import WikipediaAgent
from src.config import Config


def demo_mla_mode():
    """Demo the MLA citation mode."""
    print("=" * 80)
    print("MLA MODE DEMO")
    print("=" * 80)
    
    config = Config("config.yaml")
    agent = WikipediaAgent(config)
    
    question = "What is quantum computing?"
    print(f"\nQuestion: {question}\n")
    
    response = agent.query(question, stream=False)
    print(response)
    print("\n")


def demo_json_mode():
    """Demo the JSON structured output mode."""
    print("=" * 80)
    print("JSON MODE DEMO (Tool-Based Fact Accumulation)")
    print("=" * 80)
    
    config = Config("config.yaml")
    # Override output format to JSON
    config._config["agent"]["output_format"] = "json"
    agent = WikipediaAgent(config)
    
    question = "What is artificial intelligence?"
    print(f"\nQuestion: {question}\n")
    print("The LLM will:")
    print("1. Search for Wikipedia articles")
    print("2. Read through the content")
    print("3. Produce a structured JSON document matching FactOutput")
    print("4. The agent validates the JSON before returning it\n")
    
    response = agent.query(question, stream=False)
    
    # Parse and pretty-print the JSON
    try:
        # Response should now be pure JSON (no extraction needed)
        data = json.loads(response)
        print(json.dumps(data, indent=2))
        
        # Show structure summary
        print("\n" + "=" * 80)
        print("STRUCTURED DATA SUMMARY")
        print("=" * 80)
        print(f"Query: {data.get('query', 'N/A')}")
        print(f"Number of sources: {len(data.get('sources', []))}")
        print(f"Number of facts: {len(data.get('facts', []))}")
        print("\nSources:")
        for source in data.get('sources', []):
            print(f"  - {source.get('title')} ({source.get('id')})")
        print("\nFact Categories:")
        categories = {}
        for fact in data.get('facts', []):
            cat = fact.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in categories.items():
            print(f"  - {cat}: {count} facts")
        
        print("\nSample Facts:")
        for i, fact in enumerate(data.get('facts', [])[:5], 1):  # Show first 5
            print(f"\n{i}. [{fact.get('category')}]")
            print(f"   {fact.get('fact')}")
            print(f"   Sources: {', '.join(fact.get('source_ids', []))}")
    except json.JSONDecodeError as e:
        print(f"Could not parse JSON: {e}")
        print("\nRaw response:")
        print(response[:500])
    except Exception as e:
        print(f"Error: {e}")
        print("\nRaw response:")
        print(response[:500])
    
    print("\n")


if __name__ == "__main__":
    print("\n")
    print("Wikipedia Agent - Output Format Comparison")
    print("=" * 80)
    print("\nThis demo shows the difference between MLA and JSON output modes.")
    print("\nJSON mode now uses Strands' structured FactOutput contract:")
    print("- The LLM reads articles and emits the required fields")
    print("- The agent enforces FactOutput via structured_output_model")
    print("- The response is validated JSON with sources, facts, and summary")
    print("\nMake sure you have configured your LLM provider in config.yaml\n")
    
    try:
        demo_mla_mode()
        demo_json_mode()
        
        print("=" * 80)
        print("DEMO COMPLETE")
        print("=" * 80)
        print("\nKey Advantages of Tool-Based Approach:")
        print("  ✓ Guaranteed valid JSON (no parsing errors)")
        print("  ✓ LLM focuses on understanding, not formatting")
        print("  ✓ Real-time fact tracking")
        print("  ✓ More natural for the LLM")
        print("\nTo use JSON mode in your own code:")
        print("  1. Set output_format: 'json' in config.yaml, OR")
        print("  2. Override it programmatically as shown in this demo\n")
        
    except Exception as e:
        print(f"\nError running demo: {e}")
        print("\nMake sure:")
        print("  1. Your LLM provider is configured in config.yaml")
        print("  2. API keys are set in .env (if using OpenRouter)")
        print("  3. Ollama is running (if using Ollama)")
        import traceback
        traceback.print_exc()
