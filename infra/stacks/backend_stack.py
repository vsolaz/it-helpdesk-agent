"""Backend stack: Lambda proxy to AgentCore + API Gateway."""

from os import path
from aws_cdk import (
    Stack, Duration, CfnOutput, RemovalPolicy,
    aws_lambda as _lambda, aws_apigateway as apigw,
    aws_dynamodb as dynamodb, aws_iam as iam,
)
from constructs import Construct

AGENTCORE_ARN = "arn:aws:bedrock-agentcore:us-east-1:903026258626:runtime/musa_helpdesk_strands-KaU5kjAIQs"

class BackendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        sessions_table = dynamodb.Table(self, "SessionsTable", table_name="helpdesk-sessions",
            partition_key=dynamodb.Attribute(name="session_id", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST, removal_policy=RemovalPolicy.DESTROY, time_to_live_attribute="ttl")
        backend_fn = _lambda.Function(self, "BackendFunction", function_name="helpdesk-backend",
            runtime=_lambda.Runtime.PYTHON_3_12, handler="lambda_handler.handler",
            code=_lambda.Code.from_asset(path.join(path.dirname(__file__), "..", "..", "agent"),
                exclude=["__pycache__", "*.pyc", "test_*", "nodes.py", "graph.py", "servicenow_tool.py",
                         "urgency_mapper.py", "field_validation.py", "dynamo_session_repository.py",
                         "session_repository.py", "models.py", "app.py"]),
            timeout=Duration.seconds(120), memory_size=256,
            environment={"AGENTCORE_AGENT_ARN": AGENTCORE_ARN, "SESSIONS_TABLE": sessions_table.table_name})
        sessions_table.grant_read_write_data(backend_fn)
        backend_fn.add_to_role_policy(iam.PolicyStatement(
            actions=["bedrock-agentcore:InvokeAgentRuntime"],
            resources=[AGENTCORE_ARN, f"{AGENTCORE_ARN}/*", f"{AGENTCORE_ARN}/runtime-endpoint/*"]))
        api = apigw.LambdaRestApi(self, "HelpdeskApi", handler=backend_fn, rest_api_name="helpdesk-api",
            default_cors_preflight_options=apigw.CorsOptions(allow_origins=apigw.Cors.ALL_ORIGINS, allow_methods=apigw.Cors.ALL_METHODS))
        self.api_url = api.url
        CfnOutput(self, "ApiUrl", value=api.url)
        CfnOutput(self, "AgentCoreArn", value=AGENTCORE_ARN)
