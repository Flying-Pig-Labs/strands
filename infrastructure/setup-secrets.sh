#!/bin/bash

# Strands Richmond Demo - Secrets Setup Script
# Configures API keys in AWS Secrets Manager

set -e

echo "🔐 Setting up API keys in AWS Secrets Manager..."

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if AWS CLI is configured with personal profile
if ! aws sts get-caller-identity --profile personal > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS profile 'personal' not configured or invalid.${NC}"
    exit 1
fi

# Get the secret ARN from stack outputs
SECRET_ARN=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`SecretsManagerArn`].OutputValue' --output text 2>/dev/null)

if [ -z "$SECRET_ARN" ]; then
    echo -e "${RED}❌ Could not retrieve Secrets Manager ARN. Stack may not be deployed.${NC}"
    echo "Please deploy the infrastructure first: ./deploy.sh"
    exit 1
fi

echo -e "${GREEN}✅ Found Secrets Manager secret: $(basename $SECRET_ARN)${NC}"

# Prompt for Claude API key
echo -e "\n${BLUE}📝 Please provide your API keys:${NC}"

read -p "Enter your Claude/Anthropic API key (sk-ant-...): " ANTHROPIC_API_KEY

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}❌ Anthropic API key is required${NC}"
    exit 1
fi

# Optional: OpenAI API key for fallback
read -p "Enter your OpenAI API key (optional for fallback): " OPENAI_API_KEY

# Create the secret JSON
SECRET_JSON="{
    \"anthropic_api_key\": \"$ANTHROPIC_API_KEY\",
    \"aws_bedrock_region\": \"us-east-1\""

if [ ! -z "$OPENAI_API_KEY" ]; then
    SECRET_JSON="$SECRET_JSON,
    \"openai_api_key\": \"$OPENAI_API_KEY\""
fi

SECRET_JSON="$SECRET_JSON
}"

echo -e "\n${BLUE}🔄 Updating secret in AWS Secrets Manager...${NC}"

# Update the secret
aws secretsmanager update-secret \
    --secret-id "$SECRET_ARN" \
    --secret-string "$SECRET_JSON" \
    --profile personal

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ API keys updated successfully in Secrets Manager${NC}"
else
    echo -e "${RED}❌ Failed to update API keys${NC}"
    exit 1
fi

# Test access to the secret
echo -e "\n${BLUE}🧪 Testing secret access...${NC}"
TEST_SECRET=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ARN" --profile personal --query 'SecretString' --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Secret access test successful${NC}"
    echo "Secret contains:"
    echo "$TEST_SECRET" | jq 'keys' 2>/dev/null || echo "- Keys configured but jq not available for display"
else
    echo -e "${RED}❌ Secret access test failed${NC}"
fi

echo -e "\n${GREEN}🎉 API key setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Test the API health: ./test-api.sh"
echo "2. Seed Richmond data: curl -X POST \$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==\`ApiGatewayUrl\`].OutputValue' --output text)seed-data"
echo "3. Query the agent: ./test-api.sh"