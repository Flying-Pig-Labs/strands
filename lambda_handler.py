"""
AWS Lambda Handler for Richmond AI Agent Demo

This module provides the Lambda function handler for the API Gateway integration,
processing HTTP requests and returning responses from the Richmond AI agent.
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

import boto3
from aws_lambda_powertools import Logger, Tracer, Metrics
from aws_lambda_powertools.logging import correlation_paths
from aws_lambda_powertools.metrics import MetricUnit
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.event_handler.exceptions import BadRequestError, InternalServerError

from agent import process_query_async, health_check_async, QueryRequest, AgentResponse

# Initialize AWS Lambda Powertools
logger = Logger()
tracer = Tracer()
metrics = Metrics()
app = APIGatewayRestResolver()

# CORS headers
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
}


@app.post("/ask")
@tracer.capture_method
def handle_ask():
    """
    Handle POST /ask requests for agent queries
    
    Expected request body:
    {
        "query": "What's the next tech meetup in Richmond?",
        "context": {} // optional
    }
    """
    try:
        # Parse request body
        body = app.current_event.json_body
        
        if not body or 'query' not in body:
            raise BadRequestError("Missing required 'query' field in request body")
        
        query = body.get('query', '').strip()
        if not query:
            raise BadRequestError("Query cannot be empty")
        
        context = body.get('context', {})
        
        logger.info("Processing agent query", extra={"query": query, "context": context})
        metrics.add_metric(name="QueryReceived", unit=MetricUnit.Count, value=1)
        
        # Process query with agent (run async in sync context)
        try:
            response_data = asyncio.run(process_query_async(query, context))
            
            # Log response metadata
            if response_data.get('error'):
                logger.error("Agent returned error", extra={"error": response_data['error']})
                metrics.add_metric(name="QueryError", unit=MetricUnit.Count, value=1)
            else:
                logger.info("Query processed successfully", extra={
                    "tools_used": response_data.get('tools_used', []),
                    "response_length": len(response_data.get('response', ''))
                })
                metrics.add_metric(name="QuerySuccess", unit=MetricUnit.Count, value=1)
                
                # Track tool usage
                for tool in response_data.get('tools_used', []):
                    metrics.add_metric(name=f"ToolUsed_{tool}", unit=MetricUnit.Count, value=1)
            
            # Add request metadata
            response_data['request_id'] = app.lambda_context.aws_request_id
            response_data['timestamp'] = datetime.utcnow().isoformat()
            
            return {
                "statusCode": 200,
                "headers": CORS_HEADERS,
                "body": json.dumps(response_data)
            }
            
        except Exception as e:
            logger.error("Error processing agent query", extra={"error": str(e)})
            metrics.add_metric(name="ProcessingError", unit=MetricUnit.Count, value=1)
            raise InternalServerError(f"Error processing query: {str(e)}")
        
    except BadRequestError:
        raise
    except Exception as e:
        logger.error("Unexpected error in ask handler", extra={"error": str(e)})
        metrics.add_metric(name="UnexpectedError", unit=MetricUnit.Count, value=1)
        raise InternalServerError("Internal server error")


@app.get("/health")
@tracer.capture_method
def handle_health():
    """
    Handle GET /health requests for health checks
    """
    try:
        logger.info("Health check requested")
        metrics.add_metric(name="HealthCheckRequested", unit=MetricUnit.Count, value=1)
        
        # Run health check
        health_data = asyncio.run(health_check_async())
        
        # Determine HTTP status based on health status
        status_code = 200
        if health_data.get('status') == 'degraded':
            status_code = 200  # Still accessible but with issues
        elif health_data.get('status') == 'unhealthy':
            status_code = 503  # Service unavailable
        
        # Add metadata
        health_data['timestamp'] = datetime.utcnow().isoformat()
        health_data['request_id'] = app.lambda_context.aws_request_id
        health_data['lambda_version'] = app.lambda_context.function_version
        
        logger.info("Health check completed", extra={"health_status": health_data['status']})
        metrics.add_metric(name="HealthCheckCompleted", unit=MetricUnit.Count, value=1)
        
        return {
            "statusCode": status_code,
            "headers": CORS_HEADERS,
            "body": json.dumps(health_data)
        }
        
    except Exception as e:
        logger.error("Error during health check", extra={"error": str(e)})
        metrics.add_metric(name="HealthCheckError", unit=MetricUnit.Count, value=1)
        return {
            "statusCode": 503,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })
        }


@app.options("/ask")
@app.options("/health")
def handle_cors():
    """Handle CORS preflight requests"""
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS
    }


@app.get("/")
def handle_root():
    """Handle root path requests"""
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": json.dumps({
            "service": "Richmond AI Agent",
            "version": "1.0.0",
            "description": "MCP + Strands AI Agent Demo for Richmond, VA",
            "endpoints": {
                "POST /ask": "Submit queries about Richmond",
                "GET /health": "Health check endpoint",
                "GET /": "This information page"
            },
            "example_request": {
                "url": "/ask",
                "method": "POST",
                "body": {
                    "query": "What's the next tech meetup in Richmond?",
                    "context": {}
                }
            }
        })
    }


@logger.inject_lambda_context(correlation_id_path=correlation_paths.API_GATEWAY_REST)
@tracer.capture_lambda_handler
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event, context):
    """
    Main Lambda handler function
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response
    """
    try:
        # Log the incoming event for debugging
        logger.debug("Received event", extra={"event": event})
        
        # Process the request through the API Gateway resolver
        return app.resolve(event, context)
        
    except Exception as e:
        logger.error("Unhandled error in lambda_handler", extra={"error": str(e)})
        metrics.add_metric(name="LambdaHandlerError", unit=MetricUnit.Count, value=1)
        
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "request_id": context.aws_request_id if context else None,
                "timestamp": datetime.utcnow().isoformat()
            })
        }


# For local testing
if __name__ == "__main__":
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    import asyncio
    
    # Create FastAPI app for local testing
    test_app = FastAPI(title="Richmond AI Agent", version="1.0.0")
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @test_app.post("/ask")
    async def test_ask(request: dict):
        """Test endpoint for local development"""
        try:
            query = request.get('query')
            context = request.get('context', {})
            
            if not query:
                return {"error": "Missing query field"}
            
            response = await process_query_async(query, context)
            return response
            
        except Exception as e:
            return {"error": str(e)}
    
    @test_app.get("/health")
    async def test_health():
        """Test health endpoint for local development"""
        try:
            return await health_check_async()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
    
    @test_app.get("/")
    async def test_root():
        """Test root endpoint"""
        return {
            "service": "Richmond AI Agent (Local Test)",
            "version": "1.0.0",
            "endpoints": ["/ask", "/health"]
        }
    
    # Run local server
    print("Starting local test server on http://localhost:8000")
    print("Test with: curl -X POST http://localhost:8000/ask -H 'Content-Type: application/json' -d '{\"query\":\"Hello Richmond!\"}'")
    uvicorn.run(test_app, host="0.0.0.0", port=8000)