#!/usr/bin/env python3
"""
Richmond AI Demo - Local Testing

Test the demo components locally before deployment.
"""
import json
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("📦 Testing Python imports...")
    
    try:
        import boto3
        import click
        print("✅ Core dependencies imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    try:
        from cli import cli
        from agent import StrandsAgent
        print("✅ Demo modules imported")
    except ImportError as e:
        print(f"❌ Demo module import error: {e}")
        return False
    
    return True

def test_cli_help():
    """Test CLI help command"""
    print("🖥️ Testing CLI help...")
    
    try:
        from click.testing import CliRunner
        from cli import cli
        
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        
        if result.exit_code == 0:
            print("✅ CLI help works")
            return True
        else:
            print(f"❌ CLI help failed: {result.output}")
            return False
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False

def test_agent_init():
    """Test agent initialization"""
    print("🤖 Testing AI agent initialization...")
    
    try:
        from agent import StrandsAgent
        
        agent = StrandsAgent("test-key", "test-table")
        result = agent.process_query("What's the next tech meetup in Richmond?")
        
        if 'response' in result:
            print("✅ Agent processes queries")
            return True
        else:
            print(f"❌ Agent query failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Agent test error: {e}")
        return False

def test_lambda_handler():
    """Test Lambda handler locally"""
    print("⚡ Testing Lambda handler...")
    
    try:
        sys.path.append(str(Path("lambda")))
        from lambda_handler import handler
        
        # Test health check
        event = {
            'httpMethod': 'GET',
            'path': '/health'
        }
        
        result = handler(event, None)
        
        if result['statusCode'] == 200:
            print("✅ Lambda handler works")
            return True
        else:
            print(f"❌ Lambda handler failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Lambda test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Richmond AI Demo - Local Testing")
    print("=" * 40)
    print()
    
    tests = [
        test_imports,
        test_cli_help,
        test_agent_init,
        test_lambda_handler
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results")
    print("=" * 15)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Demo is ready to deploy.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())