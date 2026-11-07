#!/bin/bash
"""
Richmond AI Demo Deployment Script

Deploy the Richmond tech community AI agent to AWS using CDK.
"""

set -e

# Configuration
STAGE=${1:-dev}
PROFILE=${2:-personal}
REGION=${3:-us-east-1}
ANTHROPIC_API_KEY=${4:-}

echo "🚀 Deploying Richmond AI Demo"
echo "================================"
echo "Stage: $STAGE"
echo "Profile: $PROFILE" 
echo "Region: $REGION"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

if ! command -v cdk &> /dev/null; then
    echo "❌ AWS CDK not found. Please install it: npm install -g aws-cdk"
    exit 1
fi

if ! aws sts get-caller-identity --profile $PROFILE &> /dev/null; then
    echo "❌ AWS profile '$PROFILE' not configured or invalid"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

# CDK Bootstrap (if needed)
echo "🏗️ Bootstrapping CDK (if needed)..."
cdk bootstrap --profile $PROFILE > /dev/null 2>&1 || echo "CDK already bootstrapped"

# Set context variables
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --profile $PROFILE --query Account --output text)
export CDK_DEFAULT_REGION=$REGION

# Deploy the stack
echo "🚀 Deploying CDK stack..."

if [ -n "$ANTHROPIC_API_KEY" ]; then
    cdk deploy \
        --profile $PROFILE \
        --context stage=$STAGE \
        --context anthropic_api_key=$ANTHROPIC_API_KEY \
        --context account=$CDK_DEFAULT_ACCOUNT \
        --context region=$REGION \
        --require-approval never
else
    echo "⚠️  No Anthropic API key provided. The agent will use mock responses."
    cdk deploy \
        --profile $PROFILE \
        --context stage=$STAGE \
        --context account=$CDK_DEFAULT_ACCOUNT \
        --context region=$REGION \
        --require-approval never
fi

# Get outputs
echo "📊 Getting deployment outputs..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "RichmondAI-$STAGE" \
    --profile $PROFILE \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
    --output text)

TABLE_NAME=$(aws cloudformation describe-stacks \
    --stack-name "RichmondAI-$STAGE" \
    --profile $PROFILE \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTable`].OutputValue' \
    --output text)

echo ""
echo "🎉 Deployment completed successfully!"
echo "===================================="
echo "API Endpoint: $API_URL"
echo "DynamoDB Table: $TABLE_NAME"
echo ""
echo "💡 Next steps:"
echo "1. Seed data: curl -X POST $API_URL/seed-data"
echo "2. Test query: curl -X POST $API_URL/ask -d '{\"query\":\"What tech meetups are happening?\"}'"
echo "3. Use CLI: python ../cli.py --api-url $API_URL ask 'What tech events are in Richmond?'"
echo ""
echo "📋 Save these environment variables:"
echo "export RICHMOND_API_URL=$API_URL"
echo "export RICHMOND_TABLE_NAME=$TABLE_NAME"