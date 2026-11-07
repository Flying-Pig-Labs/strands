#!/bin/bash

# Strands Richmond Demo - CDK Destruction Script
# This script safely destroys the infrastructure

set -e

echo "🗑️  Destroying Strands Richmond Demo Infrastructure..."

# Confirm destruction
read -p "Are you sure you want to destroy all resources? This action cannot be undone. (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Destruction cancelled"
    exit 0
fi

# Check if AWS CLI is configured with personal profile
if ! aws sts get-caller-identity --profile personal > /dev/null 2>&1; then
    echo "❌ AWS profile 'personal' not configured or invalid. Please check your AWS credentials."
    exit 1
fi

echo "✅ AWS profile 'personal' verified"

# Build TypeScript
echo "🔨 Building TypeScript..."
npm run build

# Destroy the stack
echo "💥 Destroying CDK stack..."
npx cdk destroy --profile personal --force

echo "✅ Infrastructure destroyed successfully!"