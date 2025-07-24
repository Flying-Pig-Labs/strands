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
from strands import Agent, MCPClient
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
    model_name: str = "claude-3-5-sonnet-20241022"
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
        
    async def initialize(self):
        """Initialize the agent with MCP tools and Claude model"""
        try:
            # Initialize Anthropic client
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
            
            self.anthropic_client = Anthropic(api_key=api_key)
            
            # Initialize MCP client for DynamoDB tools
            self.mcp_client = MCPClient()
            await self._setup_mcp_tools()
            
            # Initialize Strands agent
            self.agent = Agent(
                model_name=self.config.model_name,
                tools=await self.mcp_client.list_tools(),
                system_prompt=self._get_system_prompt(),
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            logger.info("Richmond Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise
    
    async def _setup_mcp_tools(self):
        """Setup MCP tools for DynamoDB interaction"""
        try:
            # Connect to DynamoDB MCP server
            await self.mcp_client.connect(
                server_url=self.config.mcp_server_url,
                environment={
                    'AWS_REGION': self.config.aws_region,
                    'DYNAMODB_TABLE': self.config.dynamodb_table
                }
            )
            
            # Verify tools are available
            tools = await self.mcp_client.list_tools()
            logger.info(f"Available MCP tools: {[tool.name for tool in tools]}")
            
        except Exception as e:
            logger.error(f"Failed to setup MCP tools: {e}")
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

When a user asks about Richmond-specific information, use the available DynamoDB tools to:
1. Query relevant data from the database
2. Provide accurate, up-to-date information
3. Be conversational and helpful in your responses

Available tools via MCP:
- dynamodb_get_item: Get specific items by key
- dynamodb_query: Query items with conditions
- dynamodb_scan: Scan table for items

Always try to use live data from the database when possible. If no relevant data is found, 
be honest about the limitations and suggest general Richmond resources.

Focus on being helpful, accurate, and Richmond-focused in all responses.
"""
    
    async def process_query(self, request: QueryRequest) -> AgentResponse:
        """Process a user query and return response"""
        try:
            if not self.agent:
                await self.initialize()
            
            logger.info(f"Processing query: {request.query}")
            
            # Process the query with the agent
            result = await self.agent.run(
                message=request.query,
                context=request.context or {}
            )
            
            # Extract tools used from the result
            tools_used = []
            if hasattr(result, 'tool_calls'):
                tools_used = [call.tool_name for call in result.tool_calls]
            
            response = AgentResponse(
                response=result.content,
                tools_used=tools_used,
                metadata={
                    'model': self.config.model_name,
                    'tokens_used': getattr(result, 'tokens_used', None),
                    'processing_time': getattr(result, 'processing_time', None)
                }
            )
            
            logger.info(f"Query processed successfully, tools used: {tools_used}")
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return AgentResponse(
                response="I apologize, but I encountered an error processing your request. Please try again.",
                error=str(e)
            )
    
    async def health_check(self) -> Dict[str, Any]:
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
                    tools = await self.mcp_client.list_tools()
                    health_status['components']['mcp'] = f'healthy ({len(tools)} tools available)'
                else:
                    health_status['components']['mcp'] = 'not initialized'
            except Exception as e:
                health_status['components']['mcp'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
            # Check Anthropic API
            try:
                if self.anthropic_client:
                    # Simple API test
                    await self.anthropic_client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=10,
                        messages=[{"role": "user", "content": "Hi"}]
                    )
                    health_status['components']['anthropic'] = 'healthy'
                else:
                    health_status['components']['anthropic'] = 'not initialized'
            except Exception as e:
                health_status['components']['anthropic'] = f'unhealthy: {e}'
                health_status['status'] = 'degraded'
            
        except Exception as e:
            health_status['status'] = 'unhealthy'
            health_status['error'] = str(e)
        
        return health_status
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.mcp_client:
                await self.mcp_client.disconnect()
            logger.info("Agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Global agent instance for Lambda reuse
_agent_instance: Optional[RichmondAgent] = None


async def get_agent() -> RichmondAgent:
    """Get or create agent instance (singleton pattern for Lambda)"""
    global _agent_instance
    
    if _agent_instance is None:
        config = RichmondAgentConfig(
            aws_region=os.getenv('AWS_REGION', 'us-east-1'),
            dynamodb_table=os.getenv('DYNAMODB_TABLE', 'richmond-data'),
            model_name=os.getenv('MODEL_NAME', 'claude-3-5-sonnet-20241022'),
        )
        _agent_instance = RichmondAgent(config)
        await _agent_instance.initialize()
    
    return _agent_instance


# Async helper functions for Lambda use
async def process_query_async(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Async wrapper for processing queries"""
    agent = await get_agent()
    request = QueryRequest(query=query, context=context)
    response = await agent.process_query(request)
    return response.model_dump()


async def health_check_async() -> Dict[str, Any]:
    """Async wrapper for health checks"""
    agent = await get_agent()
    return await agent.health_check()


# Sync wrappers for easier integration
def process_query_sync(query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
    """Sync wrapper for processing queries"""
    return asyncio.run(process_query_async(query, context))


def health_check_sync() -> Dict[str, Any]:
    """Sync wrapper for health checks"""
    return asyncio.run(health_check_async())


if __name__ == "__main__":
    # Test the agent locally
    async def test_agent():
        config = RichmondAgentConfig()
        agent = RichmondAgent(config)
        await agent.initialize()
        
        # Test query
        request = QueryRequest(query="What's the next tech meetup in Richmond?")
        response = await agent.process_query(request)
        print(json.dumps(response.model_dump(), indent=2))
        
        # Health check
        health = await agent.health_check()
        print(json.dumps(health, indent=2))
        
        await agent.cleanup()
    
    asyncio.run(test_agent())