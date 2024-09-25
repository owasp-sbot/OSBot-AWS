from osbot_aws.aws.s3.S3                import S3
from osbot_aws.aws.s3.S3__Minio         import S3__Minio
from osbot_aws.testing.TestCase__Dynamo_DB__Local import TestCase__Dynamo_DB__Local
from osbot_aws.testing.TestCase__Minio import TestCase__Minio
from osbot_utils.testing.Temp_Env_Vars  import Temp_Env_Vars
from unittest                           import TestCase
from osbot_utils.testing.Hook_Method    import Hook_Method
from osbot_utils.utils.Env              import get_env

TEST__AWS_ACCOUNT_ID     = '000011110000'
TEST__AWS_DEFAULT_REGION = 'eu-west-1'


class TestCase__Minio__Dynamo_DB(TestCase__Dynamo_DB__Local):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_case_minio = TestCase__Minio()
        cls.test_case_minio.setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.test_case_minio.tearDownClass()


