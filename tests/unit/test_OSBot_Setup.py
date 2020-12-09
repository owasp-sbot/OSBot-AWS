from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.OSBot_Setup import OSBot_Setup

class test_OSBot_Setup(Test_Helper):
    def setUp(self):
        self.osbot_setup = super().setUp()


    def test__init__(self):
        assert self.osbot_setup.profile_name == AWS_Config().aws_session_profile_name()

    def test_lambda_package(self):
        self.lambda_package = self.osbot_setup.lambda_package('an-lambda-name')

        assert self.lambda_package.lambda_name   == 'an-lambda-name'
        assert self.lambda_package.tmp_s3_bucket == self.osbot_setup.s3_bucket_lambdas
        assert self.lambda_package.tmp_s3_key    == 'lambdas/an-lambda-name.zip'

        #self.result = self.lambda_package.tmp_s3_key


    def test_set_up_buckets(self):
        self.result =self.osbot_setup.set_up_buckets()
        assert self.osbot_setup.s3_bucket_lambdas in self.osbot_setup.s3.buckets()


