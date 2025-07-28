from unittest                                                   import TestCase
from osbot_aws.AWS_Config                                       import AWS_Config
from osbot_aws.aws.s3.S3                                        import S3
from osbot_aws.aws.lambda_.dependencies.Lambda__Dependency__S3  import Lambda__Dependency__S3
from tests.integration.osbot_aws__objs_for__integration_tests   import setup__osbot_aws__integration_tests

from osbot_utils.utils.Dev import pprint

class test_Lambda__Dependency__S3(TestCase):

    @classmethod
    def setUpClass(cls):
        setup__osbot_aws__integration_tests()
        cls.lambda_dependency_s3 = Lambda__Dependency__S3()

    def test__init__(self):
        with self.lambda_dependency_s3 as _:
            assert type(_            )             is Lambda__Dependency__S3
            assert type(_.aws_config )             is AWS_Config
            assert type(_.s3         )             is S3
            assert type(_.s3.client()).__module__  == 'botocore.client'         # confirm it is a boto3 S3 client
            assert type(_.s3.client()).__name__    == 'S3'
            assert _.s3.client().meta.endpoint_url == 'http://localhost:4566'   # wired up to LocalStack

    def test__1__setup(self):
        with self.lambda_dependency_s3 as _:
            assert _.setup()          == _
            assert _.bucket__exists() is True

    def test_bucket__name(self):
        with self.lambda_dependency_s3 as _:
            assert _.bucket__name() == '000000000000--osbot-lambdas--us-east-1'     # default account and region values are assigned in setup__osbot_aws__integration_tests()

