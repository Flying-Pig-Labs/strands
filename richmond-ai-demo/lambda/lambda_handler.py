"""
Richmond AI Agent Lambda Handler

Main Lambda function for processing Richmond tech community queries.
"""
import json
import boto3
import os
from datetime import datetime
from typing import Dict, Any
import traceback

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for API Gateway requests"""
    
    print(f"Event: {json.dumps(event)}")
    
    try:
        # Handle CORS preflight
        if event.get('httpMethod') == 'OPTIONS':
            return cors_response({})
        
        # Route based on path and method
        path = event.get('path', '/')
        method = event.get('httpMethod', 'GET')
        
        if path == '/health' and method == 'GET':
            return handle_health()
        elif path == '/ask' and method == 'POST':
            return handle_ask(event)
        elif path == '/' and method == 'GET':
            return handle_root()
        else:
            return cors_response({
                'statusCode': 404,
                'body': json.dumps({'error': 'Not found'})
            })
            
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return cors_response({
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        })

def handle_health() -> Dict[str, Any]:
    """Health check endpoint"""
    return cors_response({
        'statusCode': 200,
        'body': json.dumps({
            'status': 'healthy',
            'service': 'Richmond AI Agent',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
    })

def handle_root() -> Dict[str, Any]:
    """Root endpoint with API info"""
    return cors_response({
        'statusCode': 200,
        'body': json.dumps({
            'service': 'Richmond AI Agent API',
            'version': '1.0.0',
            'endpoints': {
                'POST /ask': 'Query the AI agent',
                'GET /health': 'Health check',
                'POST /seed-data': 'Load sample data'
            },
            'demo_query': "What's the next tech meetup in Richmond?"
        })
    })

def handle_ask(event: Dict[str, Any]) -> Dict[str, Any]:
    """Handle AI agent query requests"""
    
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        query = body.get('query', '')
        
        if not query:
            return cors_response({
                'statusCode': 400,
                'body': json.dumps({'error': 'Query is required'})
            })
        
        # Process with AI agent
        result = process_ai_query(query)
        
        return cors_response({
            'statusCode': 200,
            'body': json.dumps(result)
        })
        
    except json.JSONDecodeError:
        return cors_response({
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        })

def process_ai_query(query: str) -> Dict[str, Any]:
    """Process query using AI agent (simplified for demo)"""
    
    # Simulate AI processing
    query_lower = query.lower()
    
    # Mock responses based on common queries
    if 'meetup' in query_lower or 'event' in query_lower:
        response = get_events_response()
    elif 'company' in query_lower or 'hiring' in query_lower:
        response = get_companies_response()
    elif 'python' in query_lower:
        response = get_python_response()
    elif 'aws' in query_lower:
        response = get_aws_response()
    else:
        response = get_general_response()
    
    # Add context from DynamoDB
    context_data = get_richmond_data()
    
    return {
        'response': response,
        'context': f"Based on {len(context_data)} Richmond tech community data points",
        'sources': ['Richmond Tech Calendar', 'Local Meetup Groups', 'Tech Companies'],
        'timestamp': datetime.now().isoformat(),
        'query': query
    }

def get_events_response() -> str:
    """Response for event-related queries"""
    return ("The next Richmond tech meetup is 'Serverless Architecture Best Practices' "
            "happening on July 27th at Startup Virginia. Alex Thompson from Capital One "
            "will be speaking about building scalable serverless applications on AWS Lambda. "
            "The event starts at 6:30 PM and includes networking and food.")

def get_companies_response() -> str:
    """Response for company-related queries"""
    return ("Richmond has a thriving tech scene with major companies like Capital One, "
            "CarMax, and Dominion Energy leading innovation. Startups like Flying Pig Labs "
            "and Booz Allen Hamilton also offer great opportunities. The city has over "
            "90,000 tech employees across various industries.")

def get_python_response() -> str:
    """Response for Python-related queries"""
    return ("The Richmond Python group meets monthly at Common House RVA and has 180+ "
            "active members. They host workshops, lightning talks, and networking events. "
            "Recent topics included data science with pandas, web scraping, and Django deployment.")

def get_aws_response() -> str:
    """Response for AWS-related queries"""
    return ("RVA Cloud Wranglers is the premier AWS meetup group in Richmond with 220+ members. "
            "They meet at VCU Engineering and feature speakers from local companies sharing "
            "real-world cloud architecture experiences. Upcoming topics include serverless, "
            "container orchestration, and cost optimization.")

def get_general_response() -> str:
    """General response about Richmond tech scene"""
    return ("Richmond's tech community is vibrant and growing! With 5+ active meetup groups, "
            "major tech employers, and innovative startups, there's something for everyone. "
            "Popular venues include Common House, Startup Virginia, and VCU Engineering. "
            "The community is welcoming to both newcomers and experienced professionals.")

def get_richmond_data() -> list:
    """Get Richmond data from DynamoDB (mock for demo)"""
    try:
        table_name = os.getenv('DYNAMODB_TABLE', 'RichmondData-dev')
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        response = table.scan(Limit=10)
        return response.get('Items', [])
        
    except Exception as e:
        print(f"DynamoDB error: {e}")
        return []

def cors_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """Add CORS headers to response"""
    return {
        **response,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Content-Type': 'application/json'
        }
    }