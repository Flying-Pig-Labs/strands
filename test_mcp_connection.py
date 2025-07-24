#!/usr/bin/env python3
"""
Test MCP connection for DynamoDB server
"""

import os
import logging
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mcp_variations():
    """Test different variations of MCP server names"""
    
    # Different package name variations to try
    variations = [
        # Direct executable name (should work based on error message)
        ("uvx", ["--from", "awslabs-dynamodb-mcp-server", "awslabs.dynamodb-mcp-server"]),
        # Original format that found 30 tools
        ("uvx", ["awslabs.dynamodb-mcp-server"]),
        ("uvx", ["awslabs.dynamodb-mcp-server@latest"]),
    ]
    
    env_vars = {
        "AWS_REGION": os.getenv('AWS_REGION', 'us-east-1'),
        "AWS_PROFILE": os.getenv('AWS_PROFILE', 'personal'),
        "DYNAMODB_TABLE": "richmond-data"
    }
    
    for cmd, args in variations:
        print(f"\n🧪 Testing command: {cmd} {' '.join(args)}")
        try:
            # Create MCP client
            mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command=cmd,
                        args=args,
                        env=env_vars
                    )
                )
            )
            
            # Test connection
            with mcp_client:
                tools = mcp_client.list_tools_sync()
                print(f"✅ Success! Found {len(tools)} tools:")
                for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                    # Handle the tool object structure properly
                    tool_name = getattr(tool, 'name', f'Tool_{i}')
                    tool_desc = getattr(tool, 'description', 'No description')
                    if hasattr(tool, 'spec') and hasattr(tool.spec, 'name'):
                        tool_name = tool.spec.name
                    if hasattr(tool, 'spec') and hasattr(tool.spec, 'description'):
                        tool_desc = tool.spec.description
                    print(f"   - {tool_name}: {tool_desc[:50]}...")
                return True, f"{cmd} {' '.join(args)}"
                
        except Exception as e:
            print(f"❌ Failed: {type(e).__name__}: {str(e)[:100]}...")
            continue
    
    return False, None

def test_direct_uvx():
    """Test if we can run uvx directly to check available packages"""
    print("\n🔍 Testing direct uvx commands...")
    
    # Test if uvx works
    os.system("uvx --version")
    
    print("\n📦 Searching for dynamodb packages...")
    # Try to find dynamodb-related packages
    os.system("uvx pip search dynamodb 2>/dev/null | grep -i mcp || echo 'No results found'")

if __name__ == "__main__":
    print("🚀 MCP Connection Test for DynamoDB")
    print("=" * 50)
    
    # Check environment
    print("🔐 Environment:")
    print(f"   AWS_PROFILE: {os.getenv('AWS_PROFILE', 'Not set')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION', 'Not set')}")
    
    # Test direct uvx
    test_direct_uvx()
    
    # Test MCP connections
    success, working_package = test_mcp_variations()
    
    if success:
        print(f"\n🎉 Success! Working package name: {working_package}")
        print("Update your agent.py to use this package name.")
    else:
        print("\n⚠️  Could not connect to any DynamoDB MCP server variation.")
        print("Next steps:")
        print("1. Check if the DynamoDB MCP server is published")
        print("2. Try installing it manually: uvx install awslabs.dynamodb-mcp-server")
        print("3. Check AWS MCP documentation for correct package name")