"""
Richmond AI Demo CDK Stack

Infrastructure as Code for the Richmond tech community AI agent.
"""
from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_dynamodb as dynamodb,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    RemovalPolicy
)
from constructs import Construct

class RichmondAIStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, stage: str, anthropic_api_key: str = None, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        self.stage = stage
        
        # Create DynamoDB table for Richmond data
        self.table = dynamodb.Table(
            self, "RichmondData",
            table_name=f"RichmondData-{stage}",
            partition_key=dynamodb.Attribute(
                name="pk",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sk", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY if stage == "dev" else RemovalPolicy.RETAIN,
            point_in_time_recovery=stage == "prod"
        )
        
        # Add GSI for querying by entity type
        self.table.add_global_secondary_index(
            index_name="EntityTypeIndex",
            partition_key=dynamodb.Attribute(
                name="entity_type",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="created_at",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        # Create secret for Anthropic API key
        if anthropic_api_key:
            self.secret = secretsmanager.Secret(
                self, "AnthropicAPIKey",
                secret_name=f"richmond-ai-{stage}/anthropic-key",
                description="Anthropic API key for Claude integration",
                secret_string_value=cdk.SecretValue.unsafe_plain_text(anthropic_api_key)
            )
        
        # Create Lambda function
        self.lambda_function = _lambda.Function(
            self, "RichmondAIAgent",
            function_name=f"richmond-ai-agent-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="lambda_handler.handler",
            code=_lambda.Code.from_asset("../lambda"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DYNAMODB_TABLE": self.table.table_name,
                "STAGE": stage,
                "SECRET_NAME": self.secret.secret_name if anthropic_api_key else "",
            }
        )
        
        # Grant Lambda permissions
        self.table.grant_read_write_data(self.lambda_function)
        
        if anthropic_api_key:
            self.secret.grant_read(self.lambda_function)
        
        # Create API Gateway
        self.api = apigateway.RestApi(
            self, "RichmondAIAPI",
            rest_api_name=f"Richmond AI Agent API ({stage})",
            description=f"API for Richmond tech community AI agent - {stage}",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # Create Lambda integration
        lambda_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            request_templates={"application/json": '{"statusCode": "200"}'}
        )
        
        # Add API routes
        self.api.root.add_method("GET", lambda_integration)  # Health check
        
        ask_resource = self.api.root.add_resource("ask")
        ask_resource.add_method("POST", lambda_integration)
        
        health_resource = self.api.root.add_resource("health")
        health_resource.add_method("GET", lambda_integration)
        
        # Data seeding Lambda
        self.seed_function = _lambda.Function(
            self, "DataSeedFunction",
            function_name=f"richmond-data-seed-{stage}",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="seed_handler.handler",
            code=_lambda.Code.from_asset("../lambda"),
            timeout=Duration.seconds(60),
            memory_size=256,
            environment={
                "DYNAMODB_TABLE": self.table.table_name,
                "STAGE": stage
            }
        )
        
        self.table.grant_write_data(self.seed_function)
        
        seed_resource = self.api.root.add_resource("seed-data")
        seed_integration = apigateway.LambdaIntegration(self.seed_function)
        seed_resource.add_method("POST", seed_integration)
        
        # Output important values
        cdk.CfnOutput(
            self, "APIEndpoint",
            value=self.api.url,
            description="Richmond AI Agent API endpoint"
        )
        
        cdk.CfnOutput(
            self, "DynamoDBTable",
            value=self.table.table_name,
            description="DynamoDB table name"
        )