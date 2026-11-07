# 🚀 Richmond AI Demo - Quick Start

**One-command demo setup and run!**

## Prerequisites

1. **AWS CLI configured with `personal` profile**
2. **Python 3.8+** and **pip**
3. **AWS CDK** installed: `npm install -g aws-cdk`

## 🎯 Quick Demo (2 minutes)

```bash
# Clone/navigate to project
cd richmond-ai-demo

# Run the complete demo (installs deps, deploys, tests)
python demo.py
```

That's it! The demo script will:
1. ✅ Install Python dependencies
2. ✅ Deploy AWS infrastructure using CDK
3. ✅ Load Richmond tech community sample data
4. ✅ Test the AI agent with sample queries
5. ✅ Provide interactive demo mode

## 🧪 Manual Testing

If you prefer manual steps:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Deploy infrastructure
cd infrastructure
./deploy.sh dev personal
cd ..

# 3. Test CLI (replace YOUR_API_URL with actual endpoint)
python cli.py --api-url YOUR_API_URL ask "What's the next tech meetup in Richmond?"

# 4. Run health check
python cli.py --api-url YOUR_API_URL health

# 5. Interactive demo
python cli.py --api-url YOUR_API_URL demo
```

## 🎮 Sample Queries

- "What's the next tech meetup in Richmond?"
- "Tell me about the Richmond Python group"
- "What companies are hiring in Richmond?"
- "Where can I find AWS events this month?"
- "Tell me about the Richmond tech scene"

## 🏗️ Architecture

```
CLI → API Gateway → Lambda (Agent) → Claude 3 → MCP Tools → DynamoDB → Response
```

## 📊 Demo Features

- 🤖 **AI Agent**: Claude 3.5 Sonnet with Strands SDK
- 🔧 **MCP Integration**: Model Context Protocol for DynamoDB
- 🏢 **Richmond Data**: 5 venues, 5 companies, 5 meetup groups, 12 events
- ☁️ **AWS Serverless**: Lambda + API Gateway + DynamoDB
- 🖥️ **Python CLI**: Feature-rich command-line interface

## 🛠️ Troubleshooting

**AWS Profile Issues:**
```bash
aws configure --profile personal
```

**CDK Not Found:**
```bash
npm install -g aws-cdk
```

**Python Dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**API Not Working:**
Check CloudFormation console for deployment status and logs in CloudWatch.

## 🧹 Cleanup

```bash
cd infrastructure
cdk destroy --profile personal
```

Built by the Claude Flow swarm team! 🐝