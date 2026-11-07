#!/usr/bin/env python3
"""
Test DynamoDB MCP tools directly
"""

import os
import json
import logging
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dynamodb_tools():
    """Test DynamoDB MCP tools"""
    
    env_vars = {
        "AWS_REGION": "us-east-1",
        "AWS_PROFILE": "personal",
        # Try different environment variable names
        "DYNAMODB_TABLE": "richmond-data",
        "DYNAMODB_TABLE_NAME": "richmond-data",
        "TABLE_NAME": "richmond-data"
    }
    
    print("🚀 Testing DynamoDB MCP Tools")
    print("=" * 50)
    print(f"🔐 Environment:")
    print(f"   Table: richmond-data")
    print(f"   Region: us-east-1")
    print(f"   Profile: personal")
    
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
        
        with mcp_client:
            # List all tools
            tools = mcp_client.list_tools_sync()
            print(f"\n✅ Connected! Found {len(tools)} tools")
            
            # Get tool names properly
            tool_names = []
            for tool in tools:
                if hasattr(tool, 'tool_name'):
                    tool_names.append(tool.tool_name)
                elif hasattr(tool, 'name'):
                    tool_names.append(tool.name)
                else:
                    tool_names.append(str(tool))
            
            print("\n📋 Available DynamoDB tools:")
            for name in sorted(tool_names)[:10]:
                print(f"   - {name}")
            
            # Try to find scan tool
            scan_tools = [name for name in tool_names if 'scan' in name.lower()]
            if scan_tools:
                print(f"\n🔍 Found scan tool: {scan_tools[0]}")
                
                # Try to scan the table
                print("\n📊 Attempting to scan richmond-data table...")
                try:
                    # Try different scan patterns
                    for table_name in ["richmond-data", "richmond-tech-data"]:
                        print(f"\n   Trying table: {table_name}")
                        result = mcp_client.call_tool_sync(
                            scan_tools[0],
                            arguments={"table_name": table_name}
                        )
                        print(f"   ✅ Success! Result: {json.dumps(result, indent=2)[:200]}...")
                        break
                except Exception as e:
                    print(f"   ❌ Scan failed: {e}")
                    
                    # Try without table_name parameter
                    print("\n   Trying scan without table_name parameter...")
                    try:
                        result = mcp_client.call_tool_sync(scan_tools[0], arguments={})
                        print(f"   ✅ Success! Result: {json.dumps(result, indent=2)[:200]}...")
                    except Exception as e2:
                        print(f"   ❌ Also failed: {e2}")
            
            # Try to find query tool
            query_tools = [name for name in tool_names if 'query' in name.lower()]
            if query_tools:
                print(f"\n🔍 Found query tool: {query_tools[0]}")
                
                # Try to query meetups
                print("\n📊 Attempting to query meetups...")
                try:
                    result = mcp_client.call_tool_sync(
                        query_tools[0],
                        arguments={
                            "table_name": "richmond-data",
                            "key_condition_expression": "#t = :type",
                            "expression_attribute_names": {"#t": "type"},
                            "expression_attribute_values": {":type": {"S": "meetup"}}
                        }
                    )
                    print(f"   ✅ Success! Result: {json.dumps(result, indent=2)[:200]}...")
                except Exception as e:
                    print(f"   ❌ Query failed: {e}")
                    
    except Exception as e:
        print(f"\n❌ Failed to connect: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dynamodb_tools()