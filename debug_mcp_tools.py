#!/usr/bin/env python3
"""
Debug MCP tools to understand their structure
"""

import os
import json
import logging
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models.bedrock import BedrockModel
from mcp import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_mcp_integration():
    """Debug the MCP integration with Strands"""
    
    env_vars = {
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "personal",
        "DYNAMODB_TABLE": "richmond-data"
    }
    
    print("🔍 Debugging MCP + Strands Integration")
    print("=" * 50)
    
    try:
        # Create MCP client
        mcp_client = MCPClient(
            lambda: stdio_client(
                StdioServerParameters(
                    command="uvx",
                    args=["--from", "awslabs-dynamodb-mcp-server", "awslabs.dynamodb-mcp-server"],
                    env=env_vars
                )
            )
        )
        
        # Create Bedrock model
        model = BedrockModel(
            client_args={'region_name': 'us-east-1'},
            model_id='anthropic.claude-3-5-sonnet-20240620-v1:0',
            max_tokens=1000,
            params={'temperature': 0.1}
        )
        
        with mcp_client:
            # Get tools
            tools = mcp_client.list_tools_sync()
            print(f"\n✅ Found {len(tools)} tools")
            
            # Debug tool structure
            if tools:
                print("\n📋 First tool structure:")
                first_tool = tools[0]
                print(f"   Type: {type(first_tool)}")
                print(f"   Attributes: {dir(first_tool)}")
                
                if hasattr(first_tool, 'tool_name'):
                    print(f"   tool_name: {first_tool.tool_name}")
                if hasattr(first_tool, 'description'):
                    print(f"   description: {first_tool.description}")
                if hasattr(first_tool, 'parameters'):
                    print(f"   parameters: {first_tool.parameters}")
            
            # Create agent
            print("\n🤖 Creating Strands agent...")
            agent = Agent(
                model=model,
                tools=tools,
                system_prompt="""
                You are testing DynamoDB access. When asked about tables or data:
                1. First try to scan the 'richmond-data' table
                2. If that fails, list available tables
                3. Report what you find
                
                Available DynamoDB tools should include scan, query, list_tables, etc.
                """
            )
            
            # Test queries
            test_queries = [
                "List all DynamoDB tables",
                "Scan the richmond-data table and show me what's in it",
                "Show me all items with type='meetup' from the richmond-data table"
            ]
            
            for query in test_queries:
                print(f"\n🧪 Testing: {query}")
                try:
                    result = agent(query)
                    print(f"✅ Result: {str(result)[:200]}...")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    
    except Exception as e:
        print(f"\n❌ Failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_mcp_integration()