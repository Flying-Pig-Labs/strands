#!/bin/bash

# Strands Richmond Demo - Infrastructure Validation Script
# Validates that all AWS resources are properly configured and accessible

set -e

echo "🔍 Validating Strands Richmond Demo Infrastructure..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is configured with personal profile
if ! aws sts get-caller-identity --profile personal > /dev/null 2>&1; then
    echo -e "${RED}❌ AWS profile 'personal' not configured or invalid.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ AWS profile 'personal' verified${NC}"

# Get stack outputs
echo "📋 Fetching stack outputs..."
STACK_OUTPUTS=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs' 2>/dev/null)

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Stack 'StrandsDemoStack' not found. Please deploy first.${NC}"
    exit 1
fi

# Extract key values
API_URL=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="ApiGatewayUrl") | .OutputValue')
TABLE_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="DynamoDbTableName") | .OutputValue')
LAMBDA_NAME=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="LambdaFunctionName") | .OutputValue')
SECRET_ARN=$(echo $STACK_OUTPUTS | jq -r '.[] | select(.OutputKey=="SecretsManagerArn") | .OutputValue')

echo -e "${GREEN}✅ Stack outputs retrieved${NC}"

# Validate DynamoDB table
echo "🗄️  Validating DynamoDB table..."
TABLE_STATUS=$(aws dynamodb describe-table --table-name $TABLE_NAME --profile personal --query 'Table.TableStatus' --output text 2>/dev/null)

if [ "$TABLE_STATUS" == "ACTIVE" ]; then
    echo -e "${GREEN}✅ DynamoDB table '$TABLE_NAME' is active${NC}"
else
    echo -e "${RED}❌ DynamoDB table '$TABLE_NAME' is not active (Status: $TABLE_STATUS)${NC}"
    exit 1
fi

# Validate Lambda function
echo "⚡ Validating Lambda function..."
LAMBDA_STATE=$(aws lambda get-function --function-name $LAMBDA_NAME --profile personal --query 'Configuration.State' --output text 2>/dev/null)

if [ "$LAMBDA_STATE" == "Active" ]; then
    echo -e "${GREEN}✅ Lambda function '$LAMBDA_NAME' is active${NC}"
else
    echo -e "${RED}❌ Lambda function '$LAMBDA_NAME' is not active (State: $LAMBDA_STATE)${NC}"
    exit 1
fi

# Validate Secrets Manager
echo "🔐 Validating Secrets Manager..."
SECRET_STATUS=$(aws secretsmanager describe-secret --secret-id $SECRET_ARN --profile personal --query 'Name' --output text 2>/dev/null)

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Secrets Manager secret is accessible${NC}"
else
    echo -e "${RED}❌ Secrets Manager secret is not accessible${NC}"
    exit 1
fi

# Test API Gateway health endpoint
echo "🌐 Testing API Gateway health endpoint..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${API_URL}health")

if [ "$HEALTH_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ API Gateway health endpoint responding${NC}"
else
    echo -e "${YELLOW}⚠️  API Gateway health endpoint returned status: $HEALTH_RESPONSE${NC}"
    echo "This might be expected if Lambda cold start takes time."
fi

# Check IAM permissions (basic test)
echo "🔑 Validating IAM permissions..."

# Test DynamoDB access
aws dynamodb scan --table-name $TABLE_NAME --limit 1 --profile personal > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ DynamoDB access permissions verified${NC}"
else
    echo -e "${RED}❌ DynamoDB access permissions failed${NC}"
fi

# Test Secrets Manager access
aws secretsmanager get-secret-value --secret-id $SECRET_ARN --profile personal > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Secrets Manager access permissions verified${NC}"
else
    echo -e "${RED}❌ Secrets Manager access permissions failed${NC}"
fi

# Display comprehensive status
echo ""
echo "📊 Infrastructure Status Summary:"
echo "================================="
echo "API Gateway URL: $API_URL"
echo "DynamoDB Table: $TABLE_NAME (Status: $TABLE_STATUS)"
echo "Lambda Function: $LAMBDA_NAME (State: $LAMBDA_STATE)"
echo "Secrets Manager: $(basename $SECRET_ARN)"
echo ""

# Check if data seeding is needed
ITEM_COUNT=$(aws dynamodb scan --table-name $TABLE_NAME --select COUNT --profile personal --query 'Count' --output text 2>/dev/null)
echo "📈 DynamoDB Items: $ITEM_COUNT"

if [ "$ITEM_COUNT" == "0" ]; then
    echo -e "${YELLOW}⚠️  DynamoDB table is empty. Consider running data seeding:${NC}"
    echo "   curl -X POST ${API_URL}seed-data"
fi

echo ""
echo -e "${GREEN}🎉 Infrastructure validation complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Set API keys in Secrets Manager:"
echo "   aws secretsmanager update-secret --secret-id $SECRET_ARN --secret-string '{\"anthropic_api_key\":\"your-key-here\"}' --profile personal"
echo ""
echo "2. Seed data (if table is empty):"
echo "   curl -X POST ${API_URL}seed-data"
echo ""
echo "3. Test the agent:"
echo "   curl -X POST ${API_URL}ask -H 'Content-Type: application/json' -d '{\"query\":\"What tech meetups are happening in Richmond?\"}'"