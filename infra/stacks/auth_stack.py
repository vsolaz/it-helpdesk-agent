"""Auth stack: Cognito User Pool for frontend authentication."""
from aws_cdk import Stack, CfnOutput, RemovalPolicy, aws_cognito as cognito
from constructs import Construct

class AuthStack(Stack):
    def __init__(self, scope, id, cloudfront_url="", **kwargs):
        super().__init__(scope, id, **kwargs)
        self.user_pool = cognito.UserPool(self, "HelpdeskUserPool", user_pool_name="helpdesk-users",
            self_sign_up_enabled=True, sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(min_length=8, require_lowercase=True, require_uppercase=True, require_digits=True, require_symbols=False),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY, removal_policy=RemovalPolicy.DESTROY)
        callback_urls = ["http://localhost:4200/callback"]
        logout_urls = ["http://localhost:4200"]
        if cloudfront_url:
            callback_urls.append(f"{cloudfront_url}/callback")
            logout_urls.append(cloudfront_url)
        self.app_client = self.user_pool.add_client("HelpdeskAppClient", user_pool_client_name="helpdesk-spa",
            generate_secret=False, auth_flows=cognito.AuthFlow(user_srp=True, user_password=True),
            o_auth=cognito.OAuthSettings(flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL, cognito.OAuthScope.PROFILE],
                callback_urls=callback_urls, logout_urls=logout_urls))
        self.domain = self.user_pool.add_domain("HelpdeskDomain", cognito_domain=cognito.CognitoDomainOptions(domain_prefix="helpdesk-mapfre"))
        CfnOutput(self, "UserPoolId", value=self.user_pool.user_pool_id)
        CfnOutput(self, "AppClientId", value=self.app_client.user_pool_client_id)
        CfnOutput(self, "CognitoDomain", value="https://helpdesk-mapfre.auth.us-east-1.amazoncognito.com")
