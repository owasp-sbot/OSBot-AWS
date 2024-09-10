from osbot_aws.aws.dynamo_db.Dynamo_DB import Dynamo_DB
from osbot_aws.aws.s3.S3 import S3
from osbot_aws.testing.TestCase__Minio__Dynamo_DB import TestCase__Minio__Dynamo_DB
from osbot_utils.utils.Functions import function_name


class test_TestCase__Minio__Dynamo_DB(TestCase__Minio__Dynamo_DB):

    @classmethod
    def setUpClass(cls):
        assert function_name(getattr(Dynamo_DB, 'client')) == 'client'
        assert function_name(getattr(S3       , 'client')) == 'client'
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert function_name(getattr(Dynamo_DB, 'client')) == 'client'
        assert function_name(getattr(S3       , 'client')) == 'client'

    def test__setUpClass(self):
        assert function_name(getattr(Dynamo_DB, 'client')) == 'wrapper_method'
        assert function_name(getattr(S3       , 'client')) == 'wrapper_method'

        assert S3       ().client().meta.endpoint_url == 'http://localhost:9000'
        assert Dynamo_DB().client().meta.endpoint_url == 'http://localhost:8000'