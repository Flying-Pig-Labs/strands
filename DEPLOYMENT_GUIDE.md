# Richmond MCP + Strands AI Agent - Deployment Guide

## DevOps Infrastructure Overview

This guide provides complete instructions for deploying the Richmond-specific MCP + Strands AI Agent demo on AWS using CDK infrastructure.

## Architecture Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   API Gateway   │───▶│   Lambda Agent   │───▶│   DynamoDB      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        
                                ▼                        
                       ┌──────────────────┐              
                       │ Secrets Manager  │              
                       └──────────────────┘              
```

### Key Infrastructure:
- **API Gateway**: REST API with `/ask`, `/health`, `/seed-data` endpoints
- **AWS Lambda**: Main agent handler + data seeder (Python 3.11)
- **DynamoDB**: Richmond tech community data (Pay-per-request)
- **Secrets Manager**: Secure Claude API key storage
- **IAM Roles**: Least-privilege access patterns
- **CloudWatch**: Centralized logging and monitoring

## Prerequisites

### 1. AWS Account Setup
```bash
# Configure AWS CLI with personal profile
aws configure --profile personal
# Enter your access key, secret key, region (us-east-1), output format (json)

# Verify configuration
aws sts get-caller-identity --profile personal
```

### 2. Development Tools
```bash
# Node.js 16+ for CDK
node --version

# AWS CDK
npm install -g aws-cdk

# Python 3.11 for Lambda
python3.11 --version

# Required for scripts
jq --version
curl --version
```

### 3. API Keys Required
- **Claude/Anthropic API Key**: For AI agent functionality (required)
- **OpenAI API Key**: For fallback/redundancy (optional)

## Quick Deployment (5 Minutes)

### Step 1: Infrastructure Deployment
```bash
cd infrastructure
./deploy.sh
```

### Step 2: Configure API Keys
```bash
./setup-secrets.sh
# Follow prompts to enter your Claude API key
```

### Step 3: Validate Deployment
```bash
./validate.sh
```

### Step 4: Test the Agent
```bash
./test-api.sh
```

## Manual Deployment Steps

### 1. Install Dependencies
```bash
cd infrastructure
npm install
```

### 2. Build Python Layer (Optional)
```bash
cd ../lambda/layers
./build-layer.sh
cd ../../infrastructure
```

### 3. Bootstrap CDK (First time only)
```bash
npx cdk bootstrap --profile personal
```

### 4. Deploy Stack
```bash
npm run build
npx cdk deploy --profile personal
```

### 5. Configure Secrets
```bash
# Get secret ARN from outputs
SECRET_ARN=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`SecretsManagerArn`].OutputValue' --output text)

# Update with your API key
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"anthropic_api_key":"your-claude-api-key-here","aws_bedrock_region":"us-east-1"}' \
  --profile personal
```

### 6. Seed Richmond Data
```bash
# Get API URL
API_URL=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' --output text)

# Seed data
curl -X POST ${API_URL}seed-data
```

## Infrastructure Details

### CDK Stack Components

#### DynamoDB Table
- **Name**: richmond-tech-data
- **Partition Key**: pk (String)
- **Sort Key**: sk (String)
- **GSI**: date-index (type, date)
- **Billing**: Pay-per-request
- **Backup**: Point-in-time recovery enabled

#### Lambda Functions
1. **Agent Lambda**:
   - Runtime: Python 3.11
   - Memory: 1024 MB
   - Timeout: 5 minutes
   - Environment: DynamoDB table, Secrets ARN

2. **Data Seed Lambda**:
   - Runtime: Python 3.11
   - Memory: 512 MB
   - Timeout: 2 minutes
   - Purpose: Populate sample Richmond data

#### API Gateway
- **Name**: Strands Richmond Demo API
- **Stage**: prod
- **CORS**: Enabled for all origins
- **Logging**: INFO level with data trace

#### Secrets Manager
- **Name**: strands-demo/api-keys
- **Fields**: anthropic_api_key, aws_bedrock_region
- **Encryption**: AWS managed keys

### IAM Security Model

#### Lambda Execution Role Permissions:
- **DynamoDB**: GetItem, PutItem, Query, Scan, UpdateItem, DeleteItem
- **Secrets Manager**: GetSecretValue
- **Bedrock**: InvokeModel (Claude 3 models)
- **CloudWatch Logs**: Basic logging

### Cost Optimization

Expected monthly costs for light usage:
- **DynamoDB**: $1-3 (pay-per-request)
- **Lambda**: $2-5 (pay-per-invocation)
- **API Gateway**: $1-3 (pay-per-request)
- **Secrets Manager**: $0.40 (per secret)
- **CloudWatch**: $1-2 (logs retention)

**Total**: $5-15/month for demo usage

## Testing and Validation

### Health Check
```bash
curl -X GET ${API_URL}health
```

### Richmond Queries
```bash
# Tech meetups
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What tech meetups are happening in Richmond?"}'

# Companies
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about tech companies in Richmond, VA"}'

# Venues
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Where do tech meetups happen in Richmond?"}'
```

### General AI Queries
```bash
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the benefits of serverless architecture?"}'
```

## Monitoring and Debugging

### CloudWatch Logs
```bash
# Main agent logs
aws logs tail /aws/lambda/$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' --output text) --profile personal --follow

# Data seed logs
aws logs tail /aws/lambda/StrandsDemoStack-DataSeedLambda* --profile personal --follow
```

### DynamoDB Data Inspection
```bash
# Get table name
TABLE_NAME=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`DynamoDbTableName`].OutputValue' --output text)

# View all data
aws dynamodb scan --table-name $TABLE_NAME --profile personal

# Query meetups specifically
aws dynamodb query \
  --table-name $TABLE_NAME \
  --index-name date-index \
  --key-condition-expression "#type = :type" \
  --expression-attribute-names '{"#type": "type"}' \
  --expression-attribute-values '{":type": {"S": "meetup"}}' \
  --profile personal
```

### API Gateway Metrics
- View in AWS Console: CloudWatch > Metrics > API Gateway
- Key metrics: Count, Latency, 4XX/5XX errors

## Troubleshooting Guide

### Common Issues

#### 1. CDK Bootstrap Required
```bash
# Error: This stack uses assets, so the toolkit stack must be deployed
npx cdk bootstrap --profile personal
```

#### 2. Lambda Cold Start Timeouts
- **Symptom**: First API calls take 15-30 seconds
- **Solution**: Expected behavior, subsequent calls will be faster
- **Mitigation**: Consider provisioned concurrency for production

#### 3. Secrets Access Denied
```bash
# Verify IAM permissions
aws iam simulate-principal-policy \
  --policy-source-arn $(aws sts get-caller-identity --profile personal --query 'Arn' --output text) \
  --action-names secretsmanager:GetSecretValue \
  --resource-arns $SECRET_ARN \
  --profile personal
```

#### 4. DynamoDB Access Issues
```bash
# Check table exists and permissions
aws dynamodb describe-table --table-name $TABLE_NAME --profile personal
```

#### 5. API Gateway CORS Errors
- **Symptom**: Browser requests fail with CORS errors
- **Solution**: CORS is configured in CDK, check browser network tab
- **Workaround**: Use curl for testing

### Performance Optimization

#### Lambda Optimization
- **Memory**: Increase from 1024MB if needed
- **Layers**: Python dependencies are in a layer for faster cold starts
- **Environment**: Minimize environment variable size

#### DynamoDB Optimization
- **Query Patterns**: Use GSI for date-based queries
- **Partition Key**: Designed for even distribution
- **Indexes**: Only necessary indexes to minimize costs

#### API Gateway Optimization
- **Caching**: Can be enabled for frequently requested data
- **Compression**: Automatic for large responses
- **Regional**: Single region for lower latency

## Security Considerations

### Network Security
- **API Gateway**: Public endpoint with CORS controls
- **Lambda**: VPC optional (not required for this demo)
- **DynamoDB**: Private AWS network only

### Data Security
- **Encryption**: All data encrypted at rest (AWS managed keys)
- **Secrets**: API keys in Secrets Manager, not environment variables
- **IAM**: Least-privilege principle applied

### Access Control
- **API**: No authentication (demo setup)
- **AWS Resources**: IAM role-based access
- **Secrets**: Role-based access only

## Production Deployment Considerations

### Security Enhancements
- **API Authentication**: Add API Gateway authorizers
- **VPC**: Deploy Lambda in private subnets
- **WAF**: Add Web Application Firewall
- **Secrets Rotation**: Enable automatic key rotation

### Performance Enhancements
- **Reserved Concurrency**: For Lambda functions
- **API Caching**: Enable response caching
- **CloudFront**: CDN for global distribution
- **DynamoDB**: Consider provisioned capacity

### Monitoring Enhancements
- **X-Ray**: Distributed tracing
- **CloudWatch Dashboards**: Custom metrics dashboards
- **Alarms**: Automated alerting
- **Log Aggregation**: Centralized log analysis

### Backup and Recovery
- **DynamoDB**: Continuous backups
- **Code**: Git repository backups
- **Infrastructure**: CDK templates in version control
- **Secrets**: Document recovery procedures

## Cleanup

### Remove All Resources
```bash
# Quick cleanup
./destroy.sh

# Manual cleanup
npx cdk destroy --profile personal --force
```

### Cost Verification
```bash
# Check for any remaining resources
aws cloudformation list-stacks --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE --profile personal | grep StrandsDemo
```

## Scripts Reference

### Provided Scripts
- `deploy.sh`: Complete infrastructure deployment
- `destroy.sh`: Safe resource cleanup
- `validate.sh`: Comprehensive infrastructure validation
- `test-api.sh`: End-to-end API testing
- `setup-secrets.sh`: Interactive API key configuration

### Available Commands
```bash
# CDK operations
npm run build          # Compile TypeScript
npm run deploy         # Deploy with personal profile
npm run diff           # Preview changes
npm run synth          # Generate CloudFormation
npm run destroy        # Destroy infrastructure

# Layer management
cd ../lambda/layers && ./build-layer.sh  # Build Python dependencies

# Validation and testing
./validate.sh          # Validate infrastructure
./test-api.sh          # Test all endpoints
./setup-secrets.sh     # Configure API keys
```

## Support and Maintenance

### Updating the Infrastructure
1. Modify CDK code in `lib/` directory
2. Run `npm run build`
3. Preview changes: `npm run diff`
4. Deploy changes: `npm run deploy`

### Updating Lambda Functions
1. Modify code in `../lambda/` directories
2. Run `npm run deploy` (CDK will redeploy functions)
3. Test changes with `./test-api.sh`

### Monitoring Health
- Use `./validate.sh` regularly to check infrastructure health
- Monitor CloudWatch logs for errors
- Set up CloudWatch alarms for production use

This deployment guide provides everything needed to successfully deploy and maintain the Richmond MCP + Strands AI Agent demo infrastructure on AWS.