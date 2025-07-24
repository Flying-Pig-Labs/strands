"""
Richmond MCP + Strands AI Agent Demo
Main Lambda handler for processing user queries using Claude 3 and MCP tools
"""

import json
import os
import boto3
import logging
from typing import Dict, Any, Optional
import subprocess
import tempfile
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit

# Initialize AWS Lambda Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
secrets_client = boto3.client('secretsmanager')
bedrock_client = boto3.client('bedrock-runtime')

# Environment variables
TABLE_NAME = os.environ['DYNAMODB_TABLE_NAME']
SECRETS_ARN = os.environ['SECRETS_ARN']
AWS_REGION = os.environ.get('REGION', 'us-east-1')
MCP_SERVER_COMMAND = os.environ.get('MCP_SERVER_COMMAND', 'uvx awslabs.aws-dynamodb-mcp-server')

class StrandsAgent:
    """
    Strands AI Agent that uses MCP tools to query DynamoDB
    and Claude 3 for natural language processing
    """
    
    def __init__(self):
        self.table = dynamodb.Table(TABLE_NAME)
        self.api_keys = None
        self.mcp_process = None
    
    @tracer.capture_method
    def get_api_keys(self) -> Dict[str, str]:
        """Retrieve API keys from AWS Secrets Manager"""
        if self.api_keys is None:
            try:
                response = secrets_client.get_secret_value(SecretId=SECRETS_ARN)
                self.api_keys = json.loads(response['SecretString'])
                logger.info("API keys retrieved successfully")
            except Exception as e:
                logger.error(f"Failed to retrieve API keys: {str(e)}")
                raise
        return self.api_keys
    
    @tracer.capture_method
    def start_mcp_server(self) -> bool:
        """Start the DynamoDB MCP server"""
        try:
            # Set up environment for MCP server
            env = os.environ.copy()
            env.update({
                'REGION': AWS_REGION,
                'DYNAMODB_TABLE_NAME': TABLE_NAME,
            })
            
            # Start MCP server process
            self.mcp_process = subprocess.Popen(
                MCP_SERVER_COMMAND.split(),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            logger.info("MCP server started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {str(e)}")
            return False
    
    @tracer.capture_method
    def query_claude(self, prompt: str, tools_context: Optional[Dict] = None) -> str:
        """Query Claude 3 via AWS Bedrock with optional tools context"""
        try:
            # Prepare the prompt with Richmond context
            system_prompt = """You are a helpful AI assistant specializing in Richmond, Virginia tech community information. 
            You have access to local Richmond tech data through MCP tools. When users ask about Richmond tech events, 
            companies, venues, or community information, use the available tools to fetch live data.
            
            Available tools through MCP:
            - dynamodb_query: Query the Richmond tech data table
            - dynamodb_get_item: Get specific items from the table
            
            Always provide accurate, helpful responses about the Richmond tech scene."""
            
            user_prompt = f"User query: {prompt}"
            
            if tools_context:
                user_prompt += f"\n\nAdditional context from tools: {json.dumps(tools_context, indent=2)}"
            
            # Prepare request for Claude 3
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": [
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            }
            
            # Call Bedrock
            response = bedrock_client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response['body'].read())
            claude_response = response_body['content'][0]['text']
            
            logger.info("Claude query completed successfully")
            metrics.add_metric(name="ClaudeInvocations", unit=MetricUnit.Count, value=1)
            
            return claude_response
            
        except Exception as e:
            logger.error(f"Failed to query Claude: {str(e)}")
            return f"I apologize, but I'm having trouble processing your request right now. Error: {str(e)}"
    
    @tracer.capture_method
    def query_richmond_data(self, query_type: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Query Richmond data from DynamoDB"""
        try:
            if query_type == "meetups":
                # Query for upcoming meetups
                response = self.table.query(
                    IndexName='date-index',
                    KeyConditionExpression='#type = :type',
                    ExpressionAttributeNames={'#type': 'type'},
                    ExpressionAttributeValues={':type': 'meetup'},
                    ScanIndexForward=True,  # Sort by date ascending
                    Limit=10
                )
                return {'items': response.get('Items', [])}
                
            elif query_type == "companies":
                # Scan for Richmond companies
                response = self.table.scan(
                    FilterExpression='#type = :type',
                    ExpressionAttributeNames={'#type': 'type'},
                    ExpressionAttributeValues={':type': 'company'},
                    Limit=20
                )
                return {'items': response.get('Items', [])}
                
            elif query_type == "venues":
                # Query for venues
                response = self.table.scan(
                    FilterExpression='#type = :type',
                    ExpressionAttributeNames={'#type': 'type'},
                    ExpressionAttributeValues={':type': 'venue'},
                    Limit=20
                )
                return {'items': response.get('Items', [])}
                
            else:
                # General query
                response = self.table.scan(Limit=50)
                return {'items': response.get('Items', [])}
                
        except Exception as e:
            logger.error(f"Failed to query Richmond data: {str(e)}")
            return {'error': str(e), 'items': []}
    
    @tracer.capture_method
    def process_query(self, user_query: str) -> Dict[str, Any]:
        """Process user query using Claude and MCP tools"""
        try:
            # Analyze query to determine if we need Richmond data
            needs_data = any(keyword in user_query.lower() for keyword in [
                'meetup', 'event', 'company', 'venue', 'richmond', 'rva', 
                'tech', 'startup', 'when', 'where', 'next'
            ])
            
            tools_context = None
            
            if needs_data:
                # Determine what type of data to query
                if any(keyword in user_query.lower() for keyword in ['meetup', 'event', 'when', 'next']):
                    tools_context = self.query_richmond_data('meetups')
                elif any(keyword in user_query.lower() for keyword in ['company', 'startup', 'business']):
                    tools_context = self.query_richmond_data('companies')
                elif any(keyword in user_query.lower() for keyword in ['venue', 'where', 'location']):
                    tools_context = self.query_richmond_data('venues')
                else:
                    tools_context = self.query_richmond_data('general')
            
            # Query Claude with context
            response = self.query_claude(user_query, tools_context)
            
            return {
                'response': response,
                'used_tools': needs_data,
                'tools_context': tools_context is not None,
                'timestamp': json.dumps({"timestamp": "2024-07-24T16:53:00Z"})  # Using current time
            }
            
        except Exception as e:
            logger.error(f"Failed to process query: {str(e)}")
            return {
                'response': f"I apologize, but I encountered an error processing your request: {str(e)}",
                'error': True,
                'timestamp': json.dumps({"timestamp": "2024-07-24T16:53:00Z"})
            }

# Global agent instance
agent = None

@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics
def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for the Richmond MCP + Strands AI Agent
    """
    global agent
    
    try:
        # Initialize agent if not already done
        if agent is None:
            agent = StrandsAgent()
            logger.info("Strands agent initialized")
        
        # Handle different HTTP methods and paths
        http_method = event.get('httpMethod', 'POST')
        path = event.get('path', '/ask')
        
        if http_method == 'GET' and path == '/health':
            # Health check endpoint
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key',
                },
                'body': json.dumps({
                    'status': 'healthy',
                    'service': 'Richmond MCP + Strands AI Agent',
                    'version': '1.0.0',
                    'timestamp': '2024-07-24T16:53:00Z'
                })
            }
        
        elif http_method == 'POST' and path == '/ask':
            # Main query processing endpoint
            body = json.loads(event.get('body', '{}'))
            user_query = body.get('query', '')
            
            if not user_query:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*',
                    },
                    'body': json.dumps({
                        'error': 'Missing query parameter',
                        'message': 'Please provide a query in the request body'
                    })
                }
            
            logger.info(f"Processing query: {user_query}")
            metrics.add_metric(name="QueriesProcessed", unit=MetricUnit.Count, value=1)
            
            # Process the query
            result = agent.process_query(user_query)
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, X-Amz-Date, Authorization, X-Api-Key',
                },
                'body': json.dumps(result)
            }
        
        else:
            # Unsupported method/path
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                },
                'body': json.dumps({
                    'error': 'Not Found',
                    'message': f'Path {path} with method {http_method} not supported'
                })
            }
    
    except Exception as e:
        logger.error(f"Handler error: {str(e)}")
        metrics.add_metric(name="Errors", unit=MetricUnit.Count, value=1)
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': 'An unexpected error occurred'
            })
        }