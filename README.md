# Richmond AI Agent - MCP + Strands Demo

A working demonstration of an AI agent using the **Model Context Protocol (MCP)** and **Strands SDK** to query live data from **Amazon DynamoDB**, powered by **Claude 3**, and deployed on **AWS Lambda + API Gateway**. The demo is tailored to **Richmond, VA** and showcases how modern AI agents interact with tools and data securely and modularly.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![AWS](https://img.shields.io/badge/AWS-Lambda%20%7C%20API%20Gateway%20%7C%20DynamoDB-orange.svg)](https://aws.amazon.com/)
[![Claude](https://img.shields.io/badge/Claude-3.5%20Sonnet-purple.svg)](https://www.anthropic.com/claude)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- AWS CLI configured
- SAM CLI installed
- Anthropic API key

### 1-Minute Setup
```bash
# Clone and setup
git clone <repository-url>
cd strands
python setup.py

# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Test locally
python test_local.py

# Deploy to AWS
./deploy.sh --stage dev --api-key $ANTHROPIC_API_KEY
```

## 🏗️ Architecture

### End-to-End Agent Flow
```
User Query → API Gateway → Lambda (Agent) → Claude 3 → MCP Tools → DynamoDB → Response
```

1. **User** submits query via API or CLI
2. **API Gateway** routes to Lambda function
3. **Agent** (running in Lambda) processes the query
4. **Claude 3** reasons about the request via Anthropic API
5. **MCP Tools** dynamically query DynamoDB when needed
6. **DynamoDB** returns live Richmond data
7. **Agent** generates final response

### Key Components

- **🤖 Agent (`agent.py`)**: Strands-powered AI agent with MCP integration
- **⚡ Lambda Handler (`lambda_handler.py`)**: AWS Lambda API integration
- **🖥️ CLI (`cli.py`)**: Command-line interface with Rich formatting
- **📊 Sample Data (`load_sample_data.py`)**: Richmond tech community data
- **🏗️ Infrastructure (`template.yaml`)**: SAM CloudFormation template

## 📋 Demo Scenario

**Query**: "What's the next tech meetup happening in Richmond?"

**Expected Flow**:
- Claude identifies need for external data
- Calls MCP tool `dynamodb_query` 
- Receives meetup data from DynamoDB
- **Response**: "The next Richmond tech meetup is RVA Cloud Wranglers on July 31st at Common House."

## 🔧 Installation & Setup

### Automated Setup
```bash
python setup.py
```

This script will:
- ✅ Check prerequisites (Python, AWS CLI, SAM CLI)
- 📦 Install dependencies in virtual environment
- 🔐 Check environment variables
- 📝 Create `.env` template
- 🧪 Optionally run local tests

### Manual Setup

1. **Install Dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Required
   export ANTHROPIC_API_KEY="your-anthropic-api-key"
   
   # Optional
   export AWS_PROFILE="your-aws-profile"
   export AWS_REGION="us-east-1" 
   ```

3. **Test Installation**
   ```bash
   python test_local.py
   ```

## 🚀 Deployment

### Deploy to AWS
```bash
# Quick deployment
./deploy.sh --stage prod --api-key $ANTHROPIC_API_KEY

# Custom deployment
./deploy.sh \
  --stage dev \
  --region us-west-2 \
  --stack-name my-richmond-agent \
  --api-key $ANTHROPIC_API_KEY \
  --model claude-3-5-sonnet-20241022
```

### Manual SAM Deployment
```bash
sam build
sam deploy --guided \
  --parameter-overrides \
    Stage=prod \
    AnthropicApiKey=$ANTHROPIC_API_KEY \
    ModelName=claude-3-5-sonnet-20241022
```

## 🖥️ Usage

### CLI Interface
```bash
# Interactive mode
python cli.py interactive

# Single query
python cli.py ask "What tech companies are in Richmond?"

# Query with context
python cli.py ask "Python meetups" --context '{"location": "downtown"}'

# Health check
python cli.py health

# Test with sample queries
python cli.py test

# Use deployed API
python cli.py --api-endpoint https://your-api.amazonaws.com/prod ask "Hello Richmond!"
```

### API Endpoints

#### POST `/ask` - Submit Query
```bash
curl -X POST https://your-api-gateway-url.amazonaws.com/prod/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What tech meetups are happening in Richmond this week?",
    "context": {}
  }'
```

#### GET `/health` - Health Check
```bash
curl https://your-api-gateway-url.amazonaws.com/prod/health
```

### Response Format
```json
{
  "response": "The next Richmond tech meetup is...",
  "tools_used": ["dynamodb_query"],
  "metadata": {
    "model": "claude-3-5-sonnet-20241022",
    "tokens_used": 150,
    "processing_time": 2.3
  },
  "request_id": "abc-123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 📊 Sample Data

The agent comes pre-loaded with Richmond tech community data:

### 🤝 Meetups & Events
- **RVA Cloud Wranglers** - AWS & Cloud Computing
- **Richmond Python User Group** - Python Development  
- **Data Science RVA** - Analytics & ML
- **RVA DevOps** - Infrastructure & Automation

### 🏢 Companies
- **Capital One** - Fintech & Digital Banking
- **CarMax** - Automotive Retail Technology
- **Flying Pig Labs** - Software Development
- **Hourly** - HR Technology Platform

### 📍 Venues
- **Common House** - Co-working & Events
- **Startup Virginia** - Startup Incubator
- **VCU Innovation Gateway** - Research Hub
- **The Frontier Project** - Creative Co-working

## 🛠️ Development

### Local Testing
```bash
# Run all tests
python test_local.py

# Test specific components
python -m pytest tests/

# Check code quality
python -m black .
python -m isort .
python -m flake8
```

### Debug Mode
```bash
# CLI with debug logging
python cli.py --debug ask "Test query"

# Lambda local testing
sam local start-api
curl http://localhost:3000/ask -d '{"query": "test"}'
```

### Adding New Data
```python
# Add to load_sample_data.py
new_item = {
    'id': str(uuid.uuid4()),
    'type': 'meetup',  # or 'company', 'venue', 'event'
    'name': 'New Richmond Meetup',
    'description': '...',
    # ... other fields
}
```

## 🏗️ Architecture Details

### MCP Integration
- **Protocol**: Model Context Protocol for tool discovery
- **Server**: DynamoDB MCP Server (`awslabs.aws-dynamodb-mcp-server`)
- **Tools**: `get_item`, `query`, `scan` operations
- **Transport**: stdio for Lambda, HTTP for development

### AWS Infrastructure
- **API Gateway**: RESTful API with CORS support
- **Lambda**: Python 3.11 runtime with 1GB memory
- **DynamoDB**: Pay-per-request billing with GSI
- **CloudWatch**: Logging and monitoring
- **IAM**: Least-privilege access roles

### Security Features
- ✅ CORS configured for web access
- ✅ IAM roles with minimal permissions
- ✅ API key encryption in transit
- ✅ VPC deployment option available
- ✅ CloudWatch audit logging

## 📈 Monitoring

### CloudWatch Dashboard
Access the auto-created dashboard:
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=RichmondAgent-prod
```

### Key Metrics
- **Lambda**: Invocations, Errors, Duration
- **API Gateway**: Request count, 4XX/5XX errors, Latency
- **DynamoDB**: Read/Write capacity, Throttles

### Logs
```bash
# Lambda logs
aws logs tail /aws/lambda/richmond-agent-prod --follow

# API Gateway logs  
aws logs tail /aws/apigateway/richmond-agent-prod --follow
```

## 🔍 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate
pip install -r requirements.txt
```

**"Invalid API key" errors**
```bash
# Check API key is set correctly
echo $ANTHROPIC_API_KEY
# Should start with 'sk-ant-'
```

**AWS deployment failures**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify SAM CLI version
sam --version  # Should be 1.70.0+
```

**DynamoDB access errors**
```bash
# Check IAM permissions
aws iam get-role-policy --role-name richmond-agent-*-role --policy-name DynamoDBCrudPolicy
```

### Debug Commands
```bash
# Test API endpoint
curl -v https://your-api.amazonaws.com/prod/health

# Check Lambda function
aws lambda invoke --function-name richmond-agent-prod --payload '{}' response.json

# Validate SAM template
sam validate --template template.yaml
```

## 🚦 Testing

### Test Queries
Try these sample queries to test the agent:

- "What's the next tech meetup in Richmond?"
- "Tell me about Capital One's tech stack"
- "Where can I host a developer event in Richmond?"
- "What Python meetups are available?"
- "Who are the major tech employers in Richmond?"

### Expected Responses
The agent should:
- ✅ Use appropriate MCP tools (check `tools_used` field)
- ✅ Return Richmond-specific information
- ✅ Respond conversationally
- ✅ Handle queries it can't answer gracefully

## 🤝 Contributing

### Development Setup
```bash
git clone <repository>
cd strands
python setup.py
pre-commit install  # Optional: git hooks
```

### Adding Features
1. **New MCP Tools**: Extend `agent.py` MCP client setup
2. **Data Types**: Add to `load_sample_data.py`
3. **API Endpoints**: Extend `lambda_handler.py`
4. **CLI Commands**: Add to `cli.py`

## 📚 References

- [Strands SDK Documentation](https://github.com/aws/strands)
- [Model Context Protocol Spec](https://modelcontextprotocol.org)
- [DynamoDB MCP Server](https://registry.modelcontextprotocol.org)
- [AWS ML Blog on MCP](https://aws.amazon.com/blogs/machine-learning/unlocking-the-power-of-mcp/)
- [Claude API Documentation](https://docs.anthropic.com/claude/reference)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏷️ Tags

`ai-agent` `mcp` `strands` `claude` `aws` `lambda` `dynamodb` `richmond` `virginia` `tech-meetups`

