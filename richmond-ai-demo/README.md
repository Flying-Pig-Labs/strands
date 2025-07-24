# Richmond AI Agent Demo

A Python CLI demo showcasing Strands SDK + MCP integration with Claude 3.5 Sonnet for Richmond tech community queries.

## Quick Start

```bash
# Clone and setup
git clone <repo>
cd richmond-ai-demo

# Install dependencies
pip install -r requirements.txt

# Set your Claude API key
export ANTHROPIC_API_KEY="your-key-here"

# Deploy infrastructure
cd infrastructure
./deploy.sh --profile personal

# Test the demo
cd ..
python cli.py ask "What's the next tech meetup in Richmond?"
```

## Demo Features

- 🤖 **AI Agent**: Claude 3.5 Sonnet with Strands SDK
- 🔧 **MCP Integration**: Model Context Protocol for DynamoDB queries
- 🏢 **Richmond Data**: Real venues, companies, meetups, and events
- ☁️ **AWS Serverless**: Lambda + API Gateway + DynamoDB
- 🖥️ **Python CLI**: Simple command-line interface

## Architecture

```
CLI → API Gateway → Lambda (Agent) → Claude 3 → MCP Tools → DynamoDB → Response
```

## Sample Queries

- "What's the next tech meetup in Richmond?"
- "Tell me about the Richmond Python group"
- "What companies are hiring in Richmond?"
- "Where can I find tech events this month?"

## Project Structure

```
richmond-ai-demo/
├── cli.py                 # Python CLI interface
├── agent.py              # Strands + MCP AI agent
├── infrastructure/       # AWS CDK deployment
├── lambda/              # Lambda function code
├── sample_data/         # Richmond tech community data
└── requirements.txt     # Python dependencies
```

Built by the Claude Flow swarm team! 🐝