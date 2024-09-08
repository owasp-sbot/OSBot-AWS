from osbot_aws.AWS_Config               import AWS_Config
from osbot_aws.aws.s3.S3                import S3
from osbot_aws.helpers.Lambda_Package   import Lambda_Package

# todo: add support for running these tests in different accounts, but for now use this to make sure we are always in the correct AWS account
CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID     = '381492182978'
CURRENT__OSBOT_AWS__TESTS__IAM_USER       = 'OSBot-AWS-Dev__Only-IAM'
CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION = 'eu-west-1'

class OSBot_Setup:      # todo refactor out this code, most of this has been moved into aws_config and Deploy_Lambda

    def __init__(self, bot_name= None, profile_name = None, account_id=None, region_name=None, lambda_s3_bucket=None, lambda_role_name=None):
        self.aws_config        = AWS_Config()
        if bot_name            : self.aws_config.set_bot_name                 (bot_name)
        if profile_name        : self.aws_config.set_aws_session_profile_name(profile_name     )
        if account_id          : self.aws_config.set_aws_session_account_id   (account_id      )
        if region_name         : self.aws_config.set_aws_session_region_name  (region_name     )
        if lambda_s3_bucket    : self.aws_config.set_lambda_s3_bucket         (lambda_s3_bucket)
        if lambda_role_name    : self.aws_config.set_lambda_role_name         (lambda_role_name)

        self.bot_name          = self.aws_config.bot_name()
        self.profile_name      = self.aws_config.aws_session_profile_name()
        self.region_name       = self.aws_config.aws_session_region_name()
        self.account_id        = self.aws_config.aws_session_account_id()
        self.s3_bucket_lambdas = self.aws_config.lambda_s3_bucket()
        self.lambda_role_name  = self.aws_config.lambda_role_name()
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
        if self.s3_bucket_lambdas not in self.s3.buckets():                         # todo: refactor to use #s3.bucket_exists()
            result = self.s3.bucket_create(self.s3_bucket_lambdas,self.region_name)
            assert result.get('status') == 'ok'
        return self



