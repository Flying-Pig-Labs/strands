"""
Richmond AI Agent - MCP + Strands Integration Demo

This module sets up a Strands AI agent that uses the Model Context Protocol (MCP)
to interact with DynamoDB for Richmond-specific data queries.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

import boto3
from strands import Agent
from strands.tools.mcp import MCPClient
from strands.models.bedrock import BedrockModel
from mcp import stdio_client, StdioServerParameters
from anthropic import Anthropic
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueryRequest(BaseModel):
    """Request model for agent queries"""
    query: str = Field(..., description="The user's question about Richmond")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")


class AgentResponse(BaseModel):
    """Response model for agent responses"""
    response: str = Field(..., description="The agent's response")
    tools_used: List[str] = Field(default_factory=list, description="Tools used in processing")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    error: Optional[str] = Field(default=None, description="Error message if any")


@dataclass
class RichmondAgentConfig:
    """Configuration for the Richmond AI Agent"""
    model_name: str = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    aws_region: str = "us-east-1"
    dynamodb_table: str = "richmond-data"
    mcp_server_url: str = "stdio://uvx awslabs.aws-dynamodb-mcp-server"
    max_tokens: int = 1000
    temperature: float = 0.1


class RichmondAgent:
    """
    AI Agent specialized for Richmond, VA queries using MCP and Strands SDK
    """
    
    def __init__(self, config: RichmondAgentConfig):
        self.config = config
        self.dynamodb = boto3.resource('dynamodb', region_name=config.aws_region)
        self.table = self.dynamodb.Table(config.dynamodb_table)
        self.anthropic_client = None
        self.mcp_client = None
        self.agent = None
        
    def initialize(self):
        """Initialize the agent with MCP tools and Claude model"""
        try:
            # Initialize Anthropic client
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            self.anthropic_client = Anthropic(api_key=api_key)
            
            # Initialize MCP client for DynamoDB tools
            self.mcp_client = MCPClient(
                lambda: stdio_client(
                    StdioServerParameters(
                        command="uvx",
                        args=["--from", "awslabs-dynamodb-mcp-server", "awslabs.dynamodb-mcp-server"],
                        env={
                            "AWS_REGION": self.config.aws_region,
                            "AWS_PROFILE": os.getenv('AWS_PROFILE', 'personal'),
                            "DYNAMODB_TABLE": self.config.dynamodb_table
                        }
                    )
                )
            )
            
            # Configure Bedrock model with correct region
            model = BedrockModel(
                client_args={
                    'region_name': self.config.aws_region  # Use us-east-1
                },
                model_id=self.config.model_name,  # claude-3-5-sonnet-20241022
                max_tokens=self.config.max_tokens,
                params={
                    'temperature': self.config.temperature
                }
            )
            
            # Initialize Strands agent with MCP tools
            with self.mcp_client:
                tools = self.mcp_client.list_tools_sync()
                self.agent = Agent(
                    model=model,
                    tools=tools,
                    system_prompt=self._get_system_prompt()
                )
            
            logger.info("Richmond Agent initialized successfully")
            if tools:
                tool_names = [tool.tool_name for tool in tools]
                logger.info(f"Available tools ({len(tools)}): {tool_names[:5]}...")
            else:
                logger.info("No tools available")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Richmond AI agent"""
        return """
You are a helpful AI assistant specializing in Richmond, Virginia information. 
You have access to a DynamoDB database containing local Richmond data including:
- Tech meetups and events
- Local companies and startups  
- Venues and locations
- Community information

The main DynamoDB table is called 'richmond-data' and contains items with a 'type' field that can be:
- 'meetup' - for tech meetups and regular gatherings
- 'company' - for local tech companies
- 'venue' - for event venues
- 'event' - for one-time events
- 'resource' - for community resources

When a user asks about Richmond-specific information:
1. Use the 'scan' tool to search the 'richmond-data' table
2. For specific queries, you can filter by type (e.g., scan for all items where type='meetup')
3. Provide accurate, up-to-date information from the database
4. Be conversational and helpful in your responses

If you encounter an error saying a table doesn't exist, try:
1. Use 'list_tables' to see available tables
2. Look for 'richmond-data' in the list
3. Use that table name in your queries

Always try to use live data from the database when possible. If no relevant data is found, 
be honest about the limitations and suggest general Richmond resources.

Focus on being helpful, accurate, and Richmond-focused in all responses.
"""
    
    def process_query(self, request: QueryRequest) -> AgentResponse:
        """Process a user query and return response"""
        try:
            if not self.agent:
                self.initialize()
            
            logger.info(f"Processing query: {request.query}")
            
            # Process the query with the agent using MCP context
            with self.mcp_client:
                result = self.agent(request.query)
            
            # Build response (Strands typically returns a simple string)
            response = AgentResponse(
                response=str(result),
                tools_used=['dynamodb_mcp_tools'],  # MCP tools were used if available
                metadata={
                    'model': self.config.model_name,
                    'query_length': len(request.query)
                }
            )
            
            logger.info(f"Query processed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return AgentResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                error=str(e)
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on agent and dependencies"""
        health_status = {
            'status': 'healthy',
            'components': {}
        }
        
        try:
            # Check DynamoDB connection
            try:
                self.table.load()
                health_status['components']['dynamodb'] = 'healthy'
            except Exception as e:
                health_status['components']['dynamodb'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Check MCP client
            try:
                if self.mcp_client:
                    with self.mcp_client:
                        tools = self.mcp_client.list_tools_sync()
                        health_status['components']['mcp'] = f'healthy ({len(tools)} tools available)'
                else:
                    health_status['components']['mcp'] = 'not initialized'
            except Exception as e:
                health_status['components']['mcp'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Check Strands agent
            try:
                if self.agent:
                    health_status['components']['strands_agent'] = 'healthy'
                else:
                    health_status['components']['strands_agent'] = 'not initialized'
            except Exception as e:
                health_status['components']['strands_agent'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # MCP client cleanup handled automatically by context manager
            logger.info("Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global agent instance for Lambda reuse
_agent_instance: Optional[RichmondAgent] = None


def get_agent() -> RichmondAgent:
    """Get or create agent instance (singleton pattern for Lambda)"""
    global _agent_instance
    
    if _agent_instance is None:
        config = RichmondAgentConfig(
            aws_region=os.getenv('AWS_REGION', 'us-east-1'),
            dynamodb_table=os.getenv('DYNAMODB_TABLE', 'richmond-data'),
            model_name=os.getenv('MODEL_NAME', 'anthropic.claude-3-5-sonnet-20240620-v1:0'),
        )
        _agent_instance = RichmondAgent(config)
        _agent_instance.initialize()
    
    return _agent_instance


# Main API functions
def process_query_sync(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Process a query using the Richmond agent"""
    agent = get_agent()
    request = QueryRequest(query=query, context=context)
    response = agent.process_query(request)
    return response.model_dump()


def health_check_sync() -> Dict[str, Any]:
    """Perform health check on the agent"""
    agent = get_agent()
    return agent.health_check()


if __name__ == "__main__":
    # Test the agent locally
    def test_agent():
        print("🚀 Testing Richmond AI Agent")
        print("=" * 40)
        
        try:
            # Test query
            print("📋 Testing query processing...")
            response = process_query_sync("What's the next tech meetup in Richmond?")
            print("✅ Query Response:")
            print(json.dumps(response, indent=2))
            
            print("\n🔍 Testing health check...")
            health = health_check_sync()
            print("✅ Health Status:")
            print(json.dumps(health, indent=2))
            
            print("\n🎉 Agent test completed successfully!")
            
        except Exception as e:
            print(f"❌ Agent test failed: {e}")
            import traceback
            traceback.print_exc()
    
    test_agent()