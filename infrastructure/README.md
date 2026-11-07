# Richmond MCP + Strands AI Agent Demo - Infrastructure

This directory contains the AWS CDK infrastructure for deploying the Richmond-specific MCP + Strands AI Agent demo on AWS.

## Architecture Overview

The infrastructure includes:

- **API Gateway**: REST API with `/ask`, `/health`, and `/seed-data` endpoints
- **AWS Lambda**: Two functions - main agent handler and data seeder
- **DynamoDB**: Richmond tech community data storage
- **Secrets Manager**: Secure API key storage (Claude/Anthropic)
- **IAM Roles**: Least-privilege access for Lambda functions
- **CloudWatch**: Logging and monitoring

## Prerequisites

1. **AWS CLI** configured with `personal` profile:
   ```bash
   aws configure --profile personal
   ```

2. **Node.js and npm** (for CDK):
   ```bash
   node --version  # Should be 16+ 
   npm --version
   ```

3. **Python 3.11** (for Lambda functions):
   ```bash
   python3.11 --version
   ```

4. **AWS CDK** installed globally:
   ```bash
   npm install -g aws-cdk
   ```

## Quick Deployment

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build Python layer** (optional - included in deployment):
   ```bash
   cd ../lambda/layers
   ./build-layer.sh
   cd ../../infrastructure
   ```

3. **Deploy infrastructure**:
   ```bash
   ./deploy.sh
   ```

4. **Validate deployment**:
   ```bash
   ./validate.sh
   ```

## Manual Deployment Steps

If you prefer manual control:

```bash
# 1. Install dependencies
npm install

# 2. Build TypeScript
npm run build

# 3. Bootstrap CDK (first time only)
npx cdk bootstrap --profile personal

# 4. Deploy stack
npx cdk deploy --profile personal

# 5. Validate deployment
./validate.sh
```

## Post-Deployment Configuration

### 1. Set API Keys in Secrets Manager

Update the secret with your Claude API key:

```bash
# Get the secret ARN from stack outputs
SECRET_ARN=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`SecretsManagerArn`].OutputValue' --output text)

# Update with your API key
aws secretsmanager update-secret \
  --secret-id $SECRET_ARN \
  --secret-string '{"anthropic_api_key":"your-claude-api-key-here","aws_bedrock_region":"us-east-1"}' \
  --profile personal
```

### 2. Seed Richmond Tech Data

Populate DynamoDB with sample Richmond tech community data:

```bash
# Get API URL from stack outputs
API_URL=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' --output text)

# Seed data
curl -X POST ${API_URL}seed-data
```

## Testing the Agent

### Health Check
```bash
curl -X GET ${API_URL}health
```

### Query the Agent
```bash
# Test Richmond-specific query
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What tech meetups are happening in Richmond?"}'

# Test general query
curl -X POST ${API_URL}ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Tell me about Richmond tech companies"}'
```

## Stack Outputs

After deployment, the stack provides these outputs:

- `ApiGatewayUrl`: API endpoint URL
- `DynamoDbTableName`: DynamoDB table name
- `SecretsManagerArn`: Secrets Manager ARN
- `LambdaFunctionName`: Main Lambda function name

## Monitoring and Debugging

### CloudWatch Logs
```bash
# View agent Lambda logs
aws logs tail /aws/lambda/$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`LambdaFunctionName`].OutputValue' --output text) --profile personal --follow

# View data seed Lambda logs
aws logs tail /aws/lambda/StrandsDemoStack-DataSeedLambda* --profile personal --follow
```

### DynamoDB Data Inspection
```bash
# Get table name
TABLE_NAME=$(aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[?OutputKey==`DynamoDbTableName`].OutputValue' --output text)

# Scan all items
aws dynamodb scan --table-name $TABLE_NAME --profile personal

# Query meetups
aws dynamodb query --table-name $TABLE_NAME --index-name date-index --key-condition-expression "#type = :type" --expression-attribute-names '{"#type": "type"}' --expression-attribute-values '{":type": {"S": "meetup"}}' --profile personal
```

## Cost Optimization

The infrastructure is designed for demo/development use with cost optimization:

- **DynamoDB**: On-demand billing mode
- **Lambda**: Pay-per-invocation with reasonable memory allocation
- **API Gateway**: Pay-per-request
- **Secrets Manager**: Single secret with minimal rotation

Expected monthly cost for light usage: **$5-15/month**

## Security Considerations

- **IAM Roles**: Least-privilege principle applied
- **API Gateway**: CORS enabled for development (restrict in production)
- **Secrets Manager**: API keys encrypted at rest
- **DynamoDB**: AWS managed encryption
- **Lambda**: Isolated execution environment

## Troubleshooting

### Common Issues

1. **CDK Bootstrap Required**:
   ```bash
   npx cdk bootstrap --profile personal
   ```

2. **Permissions Error**:
   - Verify AWS profile has necessary permissions
   - Check IAM policies for CDK deployment

3. **Layer Build Fails**:
   ```bash
   cd ../lambda/layers
   ./build-layer.sh
   ```

4. **Lambda Cold Start**:
   - First API calls may be slow (15-30 seconds)
   - Subsequent calls should be faster

### Getting Help

1. Check CloudWatch logs for detailed error messages
2. Run `./validate.sh` to verify infrastructure state
3. Use `cdk diff` to see changes before deployment
4. Review stack events in CloudFormation console

## Cleanup

To remove all resources:

```bash
./destroy.sh
```

Or manually:

```bash
npx cdk destroy --profile personal --force
```

**Note**: This will permanently delete all data and resources.

## Development

### Modifying Infrastructure

1. Edit files in `lib/` directory
2. Run `npm run build` to compile TypeScript
3. Run `cdk diff` to preview changes
4. Run `cdk deploy` to apply changes

### Lambda Function Updates

Lambda function code is in `../lambda/` directories. After changes:

1. Update the code
2. Run `cdk deploy` to update functions
3. Test the changes

### CDK Commands

```bash
npm run build          # Compile TypeScript
npm run watch          # Watch for changes
npm run test           # Run tests (if any)
npm run cdk -- diff    # Compare deployed stack with current state
npm run cdk -- synth   # Emit synthesized CloudFormation template
```

## Architecture Decisions

### Why CDK over CloudFormation/Terraform?

- **Type Safety**: TypeScript provides compile-time checking
- **AWS Integration**: Native AWS constructs and best practices
- **Maintainability**: Higher-level abstractions reduce boilerplate
- **Community**: Rich ecosystem of CDK constructs

### Why DynamoDB over RDS?

- **Serverless**: No server management required
- **Cost**: Pay-per-request pricing for demo workloads
- **Performance**: Consistent single-digit millisecond latency
- **Integration**: Native AWS Lambda integration

### Why Lambda over ECS/EC2?

- **Serverless**: No infrastructure management
- **Cost**: Pay only for execution time
- **Scaling**: Automatic scaling with zero configuration
- **Integration**: Native API Gateway integration

This infrastructure provides a robust, scalable foundation for the Richmond MCP + Strands AI Agent demo while maintaining cost efficiency and security best practices.