#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.backend_stack import BackendStack
from stacks.frontend_stack import FrontendStack

app = cdk.App()
env = cdk.Environment(region="us-east-1")
backend = BackendStack(app, "HelpdeskBackendStack", env=env)
frontend = FrontendStack(app, "HelpdeskFrontendStack", env=env, api_url=backend.api_url)
app.synth()
