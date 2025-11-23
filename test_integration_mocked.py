#!/usr/bin/env python3
"""
Integration tests with mocked LLM responses - no API calls required.

Run this locally to test agent functionality without making expensive API calls.

Usage:
    python test_integration_mocked.py
"""
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from src.agent import WikipediaAgent
from src.config import Config

print("=" * 60)
print("INTEGRATION TESTS (MOCKED - NO API CALLS)")
print("=" * 60)


def test_agent_initialization():
    """Test that agent initializes correctly with mocked model."""
    print("\n1. Testing agent initialization...")
    
    # Mock the model creation to avoid needing real credentials
    with patch('src.agent.create_model_from_config') as mock_create_model:
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        
        config = Config("config.yaml")
        agent = WikipediaAgent(config)
        
        assert agent.output_format in ["mla", "json"]
        assert agent.config == config
        print("   ✓ Agent initialized successfully")
        print(f"   ✓ Output format: {agent.output_format}")
        print(f"   ✓ Provider: {config.llm_provider}")
    return True


def test_output_format_switching():
    """Test that output format can be switched."""
    print("\n2. Testing output format switching...")
    
    with patch('src.agent.create_model_from_config') as mock_create_model:
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        
        config = Config("config.yaml")
        
        # Test MLA mode
        agent_mla = WikipediaAgent(config)
        assert agent_mla.output_format == "mla"
        print("   ✓ MLA mode configured")
        
        # Test JSON mode
        config._config["agent"]["output_format"] = "json"
        agent_json = WikipediaAgent(config)
        assert agent_json.output_format == "json"
        print("   ✓ JSON mode configured")
    return True


def test_query_with_mock():
    """Test query with mocked response."""
    print("\n3. Testing query with mocked response...")
    
    with patch('src.agent.create_model_from_config') as mock_create_model:
        mock_model = Mock()
        mock_create_model.return_value = mock_model
        
        config = Config("config.yaml")
        agent = WikipediaAgent(config)
        
        # Mock the agent's query method
        mock_response = """
        Python is a high-level programming language ("Python (programming language)").
        It was created by Guido van Rossum in 1991 ("Python (programming language)").
        
        Works Cited
        "Python (programming Language)." Wikipedia, Wikimedia Foundation, 
            en.wikipedia.org/wiki/Python_(programming_language). Accessed 22 Nov. 2025.
        """
        
        with patch.object(agent.agent, '__call__', return_value=Mock(output=mock_response)):
            response = agent.query("What is Python?", stream=False)
            
            assert len(response) > 50
            assert "Python" in response
            assert "Works Cited" in response
            print("   ✓ Query executed with mocked response")
            print(f"   ✓ Response length: {len(response)} chars")
    return True


def test_config_loading():
    """Test that config loads correctly."""
    print("\n4. Testing config loading...")
    
    config = Config("config.yaml")
    
    assert config.llm_provider in ["ollama", "openrouter"]
    assert config.output_format in ["mla", "json"]
    assert config.wikipedia_config is not None
    
    print(f"   ✓ Provider: {config.llm_provider}")
    print(f"   ✓ Output format: {config.output_format}")
    print(f"   ✓ Wikipedia language: {config.wikipedia_config.get('language')}")
    print(f"   ✓ Max articles: {config.wikipedia_config.get('max_articles')}")
    return True


def test_wikipedia_tools_available():
    """Test that Wikipedia tools are available."""
    print("\n5. Testing Wikipedia tools availability...")
    
    from src.wikipedia.tools import wikipedia_tools, wikipedia_tools_json
    
    assert len(wikipedia_tools) > 0
    assert len(wikipedia_tools_json) > 0
    
    print(f"   ✓ Standard tools: {len(wikipedia_tools)} available")
    print(f"   ✓ JSON tools: {len(wikipedia_tools_json)} available")
    
    # Check tool names
    tool_names = [tool.name for tool in wikipedia_tools]
    print(f"   ✓ Tools: {', '.join(tool_names)}")
    return True


if __name__ == "__main__":
    try:
        results = []
        results.append(("Agent Initialization", test_agent_initialization()))
        results.append(("Output Format Switching", test_output_format_switching()))
        results.append(("Query with Mock", test_query_with_mock()))
        results.append(("Config Loading", test_config_loading()))
        results.append(("Wikipedia Tools", test_wikipedia_tools_available()))
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for name, passed in results:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status} - {name}")
        
        all_passed = all(result[1] for result in results)
        print("\n" + "=" * 60)
        if all_passed:
            print("✅ ALL INTEGRATION TESTS PASSED!")
            print("\nNote: These tests use mocked LLM responses.")
            print("Run 'python test_e2e_manual.py' to test with real API.")
            print("=" * 60)
            sys.exit(0)
        else:
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
