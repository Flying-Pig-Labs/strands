#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { StrandsDemoStack } from '../lib/strands-demo-stack';

const app = new cdk.App();

// Get the AWS account and region from context or environment
const account = process.env.CDK_DEFAULT_ACCOUNT || '418272766513';
const region = process.env.CDK_DEFAULT_REGION || 'us-east-1';

new StrandsDemoStack(app, 'StrandsDemoStack', {
  env: {
    account: account,
    region: region,
  },
  description: 'Richmond MCP + Strands AI Agent Demo Infrastructure',
  tags: {
    Project: 'StrandsDemo',
    Environment: 'demo',
    Location: 'Richmond',
    Purpose: 'MCP-Strands-Integration'
  }
});