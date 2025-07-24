#!/bin/bash

# Richmond AI Agent Deployment Script
# Deploys the agent to AWS using SAM

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
STAGE="prod"
REGION="us-east-1"
STACK_NAME=""
ANTHROPIC_API_KEY=""
MODEL_NAME="claude-3-5-sonnet-20241022"

# Functions
print_banner() {
    echo -e "${BLUE}"
    echo "=================================="
    echo "  Richmond AI Agent Deployment"
    echo "  MCP + Strands Demo"
    echo "=================================="
    echo -e "${NC}"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -s, --stage STAGE          Deployment stage (dev/staging/prod) [default: prod]"
    echo "  -r, --region REGION        AWS region [default: us-east-1]"
    echo "  -n, --stack-name NAME      CloudFormation stack name [default: richmond-agent-STAGE]"
    echo "  -k, --api-key KEY          Anthropic API key (required)"
    echo "  -m, --model MODEL          Claude model name [default: claude-3-5-sonnet-20241022]"
    echo "  -h, --help                 Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  ANTHROPIC_API_KEY         Anthropic API key"
    echo "  AWS_PROFILE               AWS profile to use"
    echo ""
    echo "Examples:"
    echo "  $0 --stage dev --api-key sk-ant-..."
    echo "  $0 --stack-name my-richmond-agent --region us-west-2"
}

check_prerequisites() {
    echo -e "${YELLOW}Checking prerequisites...${NC}"
    
    # Check if SAM CLI is installed
    if ! command -v sam &> /dev/null; then
        echo -e "${RED}Error: SAM CLI is not installed${NC}"
        echo "Please install SAM CLI: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html"
        exit 1
    fi
    
    # Check if AWS CLI is configured
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}Error: AWS CLI is not configured or credentials are invalid${NC}"
        echo "Please run 'aws configure' or set up your AWS credentials"
        exit 1
    fi
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        exit 1
    fi
    
    # Check if required files exist
    local required_files=("template.yaml" "requirements.txt" "lambda_handler.py" "agent.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            echo -e "${RED}Error: Required file $file not found${NC}"
            exit 1
        fi
    done
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
}

validate_parameters() {
    # Set default stack name if not provided
    if [[ -z "$STACK_NAME" ]]; then
        STACK_NAME="richmond-agent-$STAGE"
    fi
    
    # Check for API key
    if [[ -z "$ANTHROPIC_API_KEY" ]] && [[ -z "$ANTHROPIC_API_KEY_ENV" ]]; then
        echo -e "${RED}Error: Anthropic API key is required${NC}"
        echo "Provide it using --api-key flag or ANTHROPIC_API_KEY environment variable"
        exit 1
    fi
    
    # Use environment variable if flag not provided
    if [[ -z "$ANTHROPIC_API_KEY" ]]; then
        ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY_ENV"
    fi
    
    # Validate stage
    if [[ ! "$STAGE" =~ ^(dev|staging|prod)$ ]]; then
        echo -e "${RED}Error: Invalid stage '$STAGE'. Must be dev, staging, or prod${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Parameters validated${NC}"
}

build_application() {
    echo -e "${YELLOW}Building application...${NC}"
    
    # Clean previous builds
    rm -rf .aws-sam
    
    # Build with SAM
    sam build --use-container
    
    echo -e "${GREEN}✓ Application built successfully${NC}"
}

deploy_application() {
    echo -e "${YELLOW}Deploying application...${NC}"
    
    # Deploy with SAM
    sam deploy \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --capabilities CAPABILITY_IAM \
        --parameter-overrides \
            Stage="$STAGE" \
            AnthropicApiKey="$ANTHROPIC_API_KEY" \
            ModelName="$MODEL_NAME" \
        --no-confirm-changeset \
        --no-fail-on-empty-changeset
    
    echo -e "${GREEN}✓ Application deployed successfully${NC}"
}

get_outputs() {
    echo -e "${YELLOW}Getting deployment outputs...${NC}"
    
    local api_url
    api_url=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
        --output text)
    
    local table_name
    table_name=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`DynamoDBTableName`].OutputValue' \
        --output text)
    
    local function_name
    function_name=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' \
        --output text)
    
    echo -e "${GREEN}"
    echo "=================================="
    echo "   Deployment Complete!"
    echo "=================================="
    echo -e "${NC}"
    echo "Stack Name:     $STACK_NAME"
    echo "Region:         $REGION"
    echo "Stage:          $STAGE"
    echo ""
    echo "API Endpoint:   $api_url"
    echo "DynamoDB Table: $table_name"
    echo "Lambda Function: $function_name"
    echo ""
    echo -e "${BLUE}Test Commands:${NC}"
    echo ""
    echo "# Health check"
    echo "curl $api_url/health"
    echo ""
    echo "# Ask a question"
    echo "curl -X POST $api_url/ask \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"query\": \"What tech meetups are happening in Richmond?\"}'"
    echo ""
    echo "# Using CLI"
    echo "python cli.py --api-endpoint $api_url ask \"What companies are in Richmond?\""
    echo ""
    echo -e "${BLUE}Monitoring:${NC}"
    echo "CloudWatch Logs: https://console.aws.amazon.com/cloudwatch/home?region=$REGION#logsV2:log-groups/log-group/%2Faws%2Flambda%2F$function_name"
    echo ""
}

cleanup_on_error() {
    if [[ $? -ne 0 ]]; then
        echo -e "${RED}Deployment failed! Check the error messages above.${NC}"
        echo ""
        echo "Common issues:"
        echo "- Invalid AWS credentials"
        echo "- Missing Anthropic API key"
        echo "- Insufficient IAM permissions"
        echo "- Stack name already exists"
        echo ""
        echo "For help, run: $0 --help"
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -s|--stage)
            STAGE="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -n|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -k|--api-key)
            ANTHROPIC_API_KEY="$2"
            shift 2
            ;;
        -m|--model)
            MODEL_NAME="$2"
            shift 2
            ;;
        -h|--help)
            print_usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error: Unknown option $1${NC}"
            print_usage
            exit 1
            ;;
    esac
done

# Get API key from environment if not provided via flag
ANTHROPIC_API_KEY_ENV="${ANTHROPIC_API_KEY:-$ANTHROPIC_API_KEY_ENV}"

# Set up error handling
trap cleanup_on_error EXIT

# Main execution
print_banner
check_prerequisites
validate_parameters
build_application
deploy_application
get_outputs

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"