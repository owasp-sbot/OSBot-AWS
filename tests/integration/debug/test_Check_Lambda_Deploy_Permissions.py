from unittest import TestCase

from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.apis.S3 import S3

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.STS import STS
from osbot_utils.utils.Dev import pprint


class test_Check_Lambda_Deploy_Permissions(TestCase):

    def setUp(self):
        self.aws_config  = AWS_Config()
        self.lambda_     = Lambda()
        self.s3          = S3()
        self.sts         = STS()

        self.expected_account_id = '785217600689'
        self.expected_region     = 'eu-west-1'
        self.expected_s3_prefix  = 'lambdas'
        self.expected_role_name  = None
        self.expected_s3_bucket  = f'{self.expected_account_id}-osbot-{self.expected_s3_prefix}'


    def test_aws_config(self ):
        assert self.aws_config.aws_session_account_id()  == self.expected_account_id
        assert self.aws_config.aws_session_region_name() == self.expected_region
        assert self.aws_config.lambda_role_name()        == self.expected_role_name
        assert self.aws_config.lambda_s3_key_prefix()    == self.expected_s3_prefix
        assert self.aws_config.lambda_s3_bucket()        == self.expected_s3_bucket

    def test_check_sts_credentials(self):
        assert self.sts.caller_identity_account()           == '785217600689'
        assert self.sts.check_current_session_credentials() is True
        assert self.sts.current_region_name()               == self.expected_region
