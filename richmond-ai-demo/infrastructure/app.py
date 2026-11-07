#!/usr/bin/env python3
"""
Richmond AI Demo CDK App

AWS CDK application for deploying the Richmond tech community AI agent.
"""
import aws_cdk as cdk
from constructs import Construct
from richmond_stack import RichmondAIStack

app = cdk.App()

# Get configuration from context or environment
stage = app.node.try_get_context("stage") or "dev"
anthropic_api_key = app.node.try_get_context("anthropic_api_key")

RichmondAIStack(
    app, 
    f"RichmondAI-{stage}",
    stage=stage,
    anthropic_api_key=anthropic_api_key,
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)

app.synth()