#!/bin/bash

# Strands Richmond Demo - CDK Deployment Script
# This script deploys the infrastructure with AWS profile=personal

set -e

echo "🚀 Deploying Strands Richmond Demo Infrastructure..."

# Check if AWS CLI is configured with personal profile
if ! aws sts get-caller-identity --profile personal > /dev/null 2>&1; then
    echo "❌ AWS profile 'personal' not configured or invalid. Please check your AWS credentials."
    exit 1
fi

echo "✅ AWS profile 'personal' verified"

# Install dependencies
echo "📦 Installing CDK dependencies..."
npm install

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Bootstrap CDK (if needed)
echo "🏗️  Checking CDK bootstrap..."
if ! aws cloudformation describe-stacks --stack-name CDKToolkit --profile personal > /dev/null 2>&1; then
    echo "📋 Bootstrapping CDK..."
    npx cdk bootstrap --profile personal
else
    echo "✅ CDK already bootstrapped"
fi

# Deploy the stack
echo "🚀 Deploying CDK stack..."
npx cdk deploy --profile personal --require-approval never

echo "✅ Deployment complete!"

# Display outputs
echo ""
echo "📋 Stack Outputs:"
aws cloudformation describe-stacks --stack-name StrandsDemoStack --profile personal --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table

echo ""
echo "🎉 Infrastructure deployment successful!"
echo "Next steps:"
echo "1. Set up API keys in Secrets Manager"
echo "2. Deploy Lambda functions with dependencies"
echo "3. Seed DynamoDB with Richmond data"
echo "4. Test the API endpoints"