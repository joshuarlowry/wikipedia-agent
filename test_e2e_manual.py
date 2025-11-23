#!/usr/bin/env python3
"""
Manual End-to-End Tests with Real API Calls

Run this script locally when you want to verify that both markdown and JSON
modes work correctly with real LLM API calls.

WARNING: This will make actual API calls to OpenRouter and incur costs!

Usage:
    python test_e2e_manual.py
    
    # Or test only one mode:
    python test_e2e_manual.py --markdown
    python test_e2e_manual.py --json
"""

import sys
import json
import argparse
from src.agent import WikipediaAgent
from src.config import Config


def test_markdown_mode():
    """Test markdown/MLA mode with real API."""
    print("=" * 60)
    print("MANUAL E2E TEST: MARKDOWN/MLA MODE")
    print("=" * 60)
    print("⚠️  This will make a real API call!\n")
    
    try:
        config = Config("config.yaml")
        agent = WikipediaAgent(config)
        
        # Verify MLA mode is set
        assert agent.output_format == "mla", f"Expected 'mla', got '{agent.output_format}'"
        print("✓ Output format: MLA")
        print(f"✓ Provider: {config.llm_provider}")
        
        # Test query - keep it simple to reduce costs
        question = "What is Python?"
        print(f"\nQuery: {question}")
        print("Sending request...\n")
        
        response = agent.query(question, stream=False)
        
        if not response or len(response) < 50:
            print(f"✗ Response too short or empty: {len(response)} chars")
            return False
        
        print(f"✓ Received response: {len(response)} characters")
        
        # Check for citation markers
        has_citations = "Wikipedia" in response or "Works Cited" in response
        if has_citations:
            print("✓ Response contains citations")
        else:
            print("⚠ Warning: Response may not contain citations")
        
        # Show full response
        print("\n" + "=" * 60)
        print("RESPONSE:")
        print("=" * 60)
        print(response)
        print("=" * 60)
        
        print("\n✓ MARKDOWN MODE TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_mode():
    """Test JSON mode with real API."""
    print("=" * 60)
    print("MANUAL E2E TEST: JSON MODE")
    print("=" * 60)
    print("⚠️  This will make a real API call!\n")
    
    try:
        config = Config("config.yaml")
        # Override to JSON mode
        config._config["agent"]["output_format"] = "json"
        agent = WikipediaAgent(config)
        
        # Verify JSON mode is set
        assert agent.output_format == "json", f"Expected 'json', got '{agent.output_format}'"
        print("✓ Output format: JSON")
        print(f"✓ Provider: {config.llm_provider}")
        
        # Test query - keep it simple to reduce costs
        question = "What is AI?"
        print(f"\nQuery: {question}")
        print("Sending request...\n")
        
        response = agent.query(question, stream=False)
        
        if not response or len(response) < 50:
            print(f"✗ Response too short or empty: {len(response)} chars")
            return False
        
        print(f"✓ Received response: {len(response)} characters")
        
        # Show raw response
        print("\n" + "-" * 60)
        print("RAW RESPONSE:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        # Try to parse JSON
        json_start = response.find('{')
        
        if json_start == -1:
            print("\n✗ No JSON object found in response")
            return False
        
        # Find balanced braces
        brace_count = 0
        json_end = json_start
        
        for i in range(json_start, len(response)):
            if response[i] == '{':
                brace_count += 1
            elif response[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
        
        if brace_count != 0:
            print("\n✗ Unbalanced braces in JSON response")
            return False
        
        json_str = response[json_start:json_end]
        
        try:
            data = json.loads(json_str)
            print("\n✓ Valid JSON parsed successfully")
        except json.JSONDecodeError as e:
            print(f"\n✗ JSON parse error: {e}")
            print(f"JSON string length: {len(json_str)}")
            return False
        
        # Show parsed JSON
        print("\n" + "=" * 60)
        print("PARSED JSON:")
        print("=" * 60)
        print(json.dumps(data, indent=2))
        print("=" * 60)
        
        # Validate structure
        print(f"\n✓ JSON fields present: {list(data.keys())}")
        
        if 'query' in data:
            print(f"✓ Query: {data['query']}")
        else:
            print("⚠ No 'query' field")
        
        if 'sources' in data:
            print(f"✓ Sources: {len(data.get('sources', []))} found")
            if data['sources']:
                for source in data['sources'][:3]:
                    title = source.get('title', 'Unknown') if isinstance(source, dict) else str(source)
                    print(f"   - {title}")
        else:
            print("⚠ No 'sources' field")
        
        if 'facts' in data:
            print(f"✓ Facts: {len(data.get('facts', []))} extracted")
        else:
            print("⚠ No 'facts' field")
        
        if 'summary' in data:
            print(f"✓ Summary: {len(data.get('summary', ''))} characters")
        else:
            print("⚠ No 'summary' field")
        
        print("\n✓ JSON MODE TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description="Manual E2E tests with real API calls")
    parser.add_argument("--markdown", action="store_true", help="Test only markdown mode")
    parser.add_argument("--json", action="store_true", help="Test only JSON mode")
    args = parser.parse_args()
    
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MANUAL END-TO-END API TESTS" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    print("⚠️  WARNING: This will make real API calls to your LLM provider!")
    print("   Make sure you have:")
    print("   1. Configured your LLM provider in config.yaml")
    print("   2. Set OPENROUTER_API_KEY in .env (if using OpenRouter)")
    print("   3. Started Ollama (if using Ollama)")
    print()
    
    input("Press Enter to continue or Ctrl+C to cancel...")
    print()
    
    results = []
    
    # Run requested tests
    if args.markdown or (not args.markdown and not args.json):
        results.append(("Markdown/MLA Mode", test_markdown_mode()))
    
    if args.json or (not args.markdown and not args.json):
        if results:  # Add spacing if we ran markdown test
            print("\n" * 2)
        results.append(("JSON Mode", test_json_mode()))
    
    # Summary
    print("\n" * 2)
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
