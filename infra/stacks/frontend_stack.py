"""Frontend stack: S3 bucket + CloudFront distribution for Angular SPA."""

from os import path
from aws_cdk import (
    Stack, RemovalPolicy, CfnOutput,
    aws_s3 as s3, aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront, aws_cloudfront_origins as origins,
)
from constructs import Construct

class FrontendStack(Stack):
    def __init__(self, scope: Construct, id: str, api_url: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        bucket = s3.Bucket(self, "FrontendBucket", removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True, block_public_access=s3.BlockPublicAccess.BLOCK_ALL)
        oai = cloudfront.OriginAccessIdentity(self, "OAI")
        bucket.grant_read(oai)
        distribution = cloudfront.Distribution(self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS),
            default_root_object="index.html",
            error_responses=[cloudfront.ErrorResponse(http_status=404, response_page_path="/index.html", response_http_status=200)])
        s3deploy.BucketDeployment(self, "DeployFrontend",
            sources=[s3deploy.Source.asset(path.join(path.dirname(__file__), "..", "..", "dist", "servicenow-ui", "browser"))],
            destination_bucket=bucket, distribution=distribution, distribution_paths=["/*"])
        CfnOutput(self, "CloudFrontUrl", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "ApiUrl", value=api_url)
