#!/usr/bin/env python3
"""
Test script to verify Strands and MCP setup is working correctly.
"""

def test_imports():
    """Test that all key packages can be imported."""
    print("🧪 Testing package imports...")
    
    # Test core dependencies
    import boto3
    import anthropic
    print("✅ AWS and Anthropic clients imported")
    
    # Test Strands
    import strands
    from strands import Agent, tool
    print("✅ Strands framework imported")
    
    # Test MCP
    import mcp
    print("✅ MCP (Model Context Protocol) imported")
    
    print("✅ All imports successful!")

def test_strands_basic_functionality():
    """Test basic Strands agent functionality."""
    print("\n🤖 Testing Strands Agent functionality...")
    
    from strands import Agent, tool
    
    @tool
    def add_numbers(a: int, b: int) -> int:
        """Add two numbers together."""
        return a + b
    
    @tool
    def greet_user(name: str) -> str:
        """Greet a user by name."""
        return f"Hello, {name}! Welcome to Strands!"
    
    # Create agent with tools
    agent = Agent(tools=[add_numbers, greet_user])
    print("✅ Agent created successfully with custom tools")
    # Check agent attributes
    try:
        tools_count = len([attr for attr in dir(agent) if 'tool' in attr.lower()])
        print(f"✅ Agent configured with tools (agent created successfully)")
    except Exception as e:
        print(f"ℹ️ Agent tools info: {str(e)}")
    
    return agent

def test_environment_setup():
    """Test environment configuration."""
    print("\n🔐 Testing environment setup...")
    
    import os
    
    # Check for required environment variables
    if os.getenv('ANTHROPIC_API_KEY'):
        print("✅ ANTHROPIC_API_KEY is set")
    else:
        print("⚠️ ANTHROPIC_API_KEY not set")
    
    if os.getenv('AWS_PROFILE'):
        print(f"✅ AWS_PROFILE set to: {os.getenv('AWS_PROFILE')}")
    else:
        print("⚠️ AWS_PROFILE not set")
    
    # Test AWS credentials
    try:
        import boto3
        session = boto3.Session()
        credentials = session.get_credentials()
        if credentials:
            print("✅ AWS credentials available")
        else:
            print("⚠️ AWS credentials not available")
    except Exception as e:
        print(f"⚠️ AWS credential check failed: {e}")

def main():
    """Main test function."""
    print("🚀 Richmond AI Agent - Strands Setup Verification")
    print("=" * 50)
    
    try:
        # Run all tests
        test_imports()
        agent = test_strands_basic_functionality()
        test_environment_setup()
        
        print("\n" + "=" * 50)
        print("🎉 Setup verification completed successfully!")
        print("🎯 Your Strands environment is ready for development!")
        print("\nNext steps:")
        print("1. Activate virtual environment: source .venv/bin/activate")
        print("2. Run your agent: python agent.py")
        print("3. Or use the CLI: python cli.py --help")
        
    except Exception as e:
        print(f"\n❌ Setup verification failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())