"""
Richmond AI Agent

Strands SDK + MCP integration for Richmond tech community queries.
"""
import json
import boto3
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

# MCP and Strands imports (simulated for demo)
class MCPTool:
    """Mock MCP tool for DynamoDB queries"""
    
    def __init__(self, table_name: str):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
    
    def query_events(self, filters: Dict[str, Any]) -> List[Dict]:
        """Query events from DynamoDB"""
        try:
            response = self.table.scan()
            events = response.get('Items', [])
            
            # Filter events by type
            if 'type' in filters:
                events = [e for e in events if e.get('entity_type') == filters['type']]
            
            # Sort by date
            events.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return events[:10]  # Return top 10
            
        except Exception as e:
            print(f"DynamoDB query error: {e}")
            return []

class StrandsAgent:
    """Richmond AI Agent using Strands SDK"""
    
    def __init__(self, anthropic_api_key: str, table_name: str = 'RichmondData'):
        self.api_key = anthropic_api_key
        self.mcp_tool = MCPTool(table_name)
        
        # Initialize Anthropic client (simulated)
        self.claude_client = self._init_claude_client()
    
    def _init_claude_client(self):
        """Initialize Claude client (mock for demo)"""
        try:
            from anthropic import Anthropic
            return Anthropic(api_key=self.api_key)
        except ImportError:
            # Mock client for demo
            return MockClaudeClient()
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a Richmond tech community query"""
        
        # Step 1: Analyze query intent
        intent = self._analyze_intent(query)
        
        # Step 2: Use MCP to get relevant data
        data = self._get_relevant_data(intent)
        
        # Step 3: Use Claude to generate response
        response = self._generate_response(query, data, intent)
        
        return {
            'response': response,
            'context': intent,
            'sources': [d.get('name', 'Unknown') for d in data],
            'timestamp': datetime.now().isoformat()
        }
    
    def _analyze_intent(self, query: str) -> str:
        """Analyze query intent (simplified)"""
        query_lower = query.lower()
        
        if 'meetup' in query_lower or 'event' in query_lower:
            return 'events'
        elif 'company' in query_lower or 'hiring' in query_lower:
            return 'companies'
        elif 'venue' in query_lower or 'place' in query_lower:
            return 'venues'
        else:
            return 'general'
    
    def _get_relevant_data(self, intent: str) -> List[Dict]:
        """Get relevant data using MCP tool"""
        
        filters = {}
        if intent == 'events':
            filters['type'] = 'event'
        elif intent == 'companies':
            filters['type'] = 'company'
        elif intent == 'venues':
            filters['type'] = 'venue'
        
        return self.mcp_tool.query_events(filters)
    
    def _generate_response(self, query: str, data: List[Dict], intent: str) -> str:
        """Generate response using Claude (simplified)"""
        
        if not data:
            return "I don't have specific information about that Richmond tech topic right now."
        
        # Create context for Claude
        context = f"Query: {query}\nIntent: {intent}\nData: {json.dumps(data[:3], indent=2)}"
        
        # Mock Claude response for demo
        if intent == 'events':
            if data:
                event = data[0]
                return f"The next Richmond tech event is '{event.get('name', 'Tech Event')}' happening soon. Check out the Richmond tech community calendar for more details!"
        
        elif intent == 'companies':
            company_names = [d.get('name', 'Tech Company') for d in data[:3]]
            return f"Richmond has great tech companies including {', '.join(company_names)}. These companies are actively involved in the local tech scene."
        
        else:
            return f"Richmond has a vibrant tech community with {len(data)} active organizations, events, and companies. The scene is growing rapidly with lots of opportunities for networking and learning."

class MockClaudeClient:
    """Mock Claude client for demo purposes"""
    
    def messages_create(self, **kwargs):
        """Mock message creation"""
        return MockMessage("This is a mock Claude response for the Richmond AI Agent demo.")

class MockMessage:
    def __init__(self, content):
        self.content = [MockContent(content)]

class MockContent:
    def __init__(self, text):
        self.text = text

# Demo usage
if __name__ == '__main__':
    # For local testing
    api_key = os.getenv('ANTHROPIC_API_KEY', 'demo-key')
    agent = StrandsAgent(api_key)
    
    test_query = "What's the next tech meetup in Richmond?"
    result = agent.process_query(test_query)
    
    print(json.dumps(result, indent=2))