#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.backend_stack import BackendStack
from stacks.frontend_stack import FrontendStack
from stacks.auth_stack import AuthStack

app = cdk.App()
env = cdk.Environment(region="us-east-1")
backend = BackendStack(app, "HelpdeskBackendStack", env=env)
frontend = FrontendStack(app, "HelpdeskFrontendStack", env=env, api_url=backend.api_url)
auth = AuthStack(app, "HelpdeskAuthStack", env=env, cloudfront_url="https://dltkw50j7m6il.cloudfront.net")
app.synth()
