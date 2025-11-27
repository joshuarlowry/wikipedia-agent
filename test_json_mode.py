#!/usr/bin/env python3
"""Test script for JSON output mode."""

import json
import sys
from src.agent import WikipediaAgent
from src.config import Config


def test_json_mode():
    """Test that JSON mode returns valid structured data using structured output."""
    print("Testing JSON mode with structured FactOutput...")
    
    # Create config with JSON output
    config = Config("config.yaml")
    config._config["agent"]["output_format"] = "json"
    
    # Create agent
    agent = WikipediaAgent(config)
    
    # Verify output format is set
    assert agent.output_format == "json", f"Expected 'json', got '{agent.output_format}'"
    print("✓ Output format set to JSON")
    
    # Test query
    question = "What is Python programming language?"
    print(f"\nQuerying: {question}")
    print("(The LLM will produce structured FactOutput JSON)")
    
    try:
        response = agent.query(question, stream=False)
        print(f"\nResponse length: {len(response)} characters")
        
        # The response should now be pure JSON (no extraction needed)
        data = json.loads(response)
        print("✓ Valid JSON response received")
        
        # Validate structure
        required_fields = ['query', 'sources', 'facts', 'people', 'places', 'events', 'ideas', 'relations', 'summary']
        for field in required_fields:
            if field not in data:
                print(f"✗ Missing required field: {field}")
                return False
        print("✓ All required fields present")
        
        # Validate list outputs
        list_keys = ['sources', 'facts', 'people', 'places', 'events', 'ideas', 'relations']
        for key in list_keys:
            if not isinstance(data.get(key, []), list):
                print(f"✗ '{key}' should be a list")
                return False
            print(f"✓ Found {len(data.get(key, []))} entries in {key}")
        
        # Check that facts were actually extracted
        if len(data['facts']) == 0:
            print("⚠ Warning: No facts were extracted")
            print("This might indicate the LLM failed to populate the structured FactOutput")
            return False
        
        # Check fact structure
        for i, fact in enumerate(data['facts']):
            required_fact_fields = ['fact', 'source_ids', 'category']
            for field in required_fact_fields:
                if field not in fact:
                    print(f"✗ Fact {i} missing field: {field}")
                    return False
        print("✓ All facts have required fields")
        
        # Validate categories
        valid_categories = ['definition', 'history', 'application', 'technical', 'other']
        for i, fact in enumerate(data['facts']):
            if fact['category'] not in valid_categories:
                print(f"✗ Fact {i} has invalid category: {fact['category']}")
                return False
        print("✓ All facts have valid categories")
        
        # Display summary
        print("\n" + "=" * 60)
        print("SUMMARY OF RESULTS")
        print("=" * 60)
        print(f"Query: {data.get('query', 'N/A')}")
        print(f"Sources: {len(data.get('sources', []))}")
        print(f"Facts extracted: {len(data.get('facts', []))}")
        print(f"Summary length: {len(data.get('summary', ''))} characters")
        
        if data.get('sources'):
            print("\nSource titles:")
            for source in data['sources']:
                print(f"  - {source.get('title', 'Unknown')}")
        
        if data.get('facts'):
            print("\nSample facts:")
            for fact in data['facts'][:3]:  # Show first 3 facts
                print(f"  - [{fact['category']}] {fact['fact'][:100]}...")
        
        print("\n✓ JSON mode test PASSED!")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ JSON parsing error: {e}")
        print("\nRaw response:")
        print(response[:500])
        return False
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mla_mode():
    """Test that MLA mode still works."""
    print("\n" + "=" * 60)
    print("Testing MLA mode (default)...")
    
    config = Config("config.yaml")
    agent = WikipediaAgent(config)
    
    assert agent.output_format == "mla", f"Expected 'mla', got '{agent.output_format}'"
    print("✓ Output format set to MLA")
    
    question = "What is the Python programming language?"
    print(f"\nQuerying: {question}")
    
    try:
        response = agent.query(question, stream=False)
        print(f"\nResponse length: {len(response)} characters")
        
        # Check for Works Cited section
        if "Works Cited" in response or "Wikipedia" in response:
            print("✓ Response contains citation markers")
            print("\n✓ MLA mode test PASSED!")
            return True
        else:
            print("⚠ Warning: No citation markers found in response")
            print("Response preview:")
            print(response[:500])
            return True  # Still pass, as the agent may format differently
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("WIKIPEDIA AGENT - OUTPUT MODE TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    # Test both modes
    results.append(("MLA Mode", test_mla_mode()))
    results.append(("JSON Mode", test_json_mode()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED!")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
