from osbot_aws.Globals import Globals
from osbot_aws.apis.S3 import S3
from osbot_aws.helpers.Lambda_Package import Lambda_Package


class OSBot_Setup:

    def __init__(self, bot_name= None, profile_name = None, account_id=None, region_name=None, lambda_s3_bucket=None, lambda_role_name=None):
        if bot_name            : Globals.bot_name                 = bot_name
        if profile_name        : Globals.aws_session_profile_name = profile_name
        if account_id          : Globals.aws_session_account_id   = account_id
        if region_name         : Globals.aws_session_region_name  = region_name
        if lambda_s3_bucket    : Globals.lambda_s3_bucket         = lambda_s3_bucket
        if lambda_role_name    : Globals.lambda_role_name         = lambda_role_name

        self.bot_name          = Globals.bot_name
        self.profile_name      = Globals.aws_session_profile_name
        self.region_name       = Globals.aws_session_region_name
        self.account_id        = Globals.aws_session_account_id
        self.s3_bucket_lambdas = Globals.lambda_s3_bucket
        self.lambda_role_name  = Globals.lambda_role_name
        self.lambda_role_arn   = f"arn:aws:iam::{self.account_id}:role/{self.lambda_role_name}"

        self.s3                = S3()

    def lambda_package(self, lambda_name) -> Lambda_Package:
        lambda_package               = Lambda_Package(lambda_name)
        lambda_package.tmp_s3_bucket = self.s3_bucket_lambdas                       # these four method calls need to be refactored
        lambda_package.tmp_s3_key    = 'lambdas/{0}.zip'.format(lambda_name)
        lambda_package.aws_lambda.set_s3_bucket(lambda_package.tmp_s3_bucket)
        lambda_package.aws_lambda.set_s3_key(lambda_package.tmp_s3_key)
        return lambda_package

    # def setup_test_environment(self):
    #     Globals.aws_session_profile_name = self.profile_name
    #     Globals.aws_session_region_name  = self.region_name
    #     return self

    def set_up_buckets(self):
        if self.s3_bucket_lambdas not in self.s3.buckets():
            result = self.s3.bucket_create(self.s3_bucket_lambdas,self.region_name)
            assert result.get('status') == 'ok'
        return self



