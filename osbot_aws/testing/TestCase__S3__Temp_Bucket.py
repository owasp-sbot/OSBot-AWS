from unittest                                           import TestCase
from osbot_local_stack.local_stack.Local_Stack          import Local_Stack
from osbot_aws.AWS_Config                               import aws_config
from osbot_aws.aws.s3.S3                                import S3
from osbot_aws.testing.Temp__Random__AWS_Credentials    import Temp__Random__AWS_Credentials
from osbot_utils.utils.Misc                             import random_uuid_short


class TestCase__S3__Temp_Bucket(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.local_stack = Local_Stack().activate()
        assert cls.local_stack.is_local_stack_configured_and_available() is True
        cls.random_aws_creds  = Temp__Random__AWS_Credentials().set_vars()
        cls.temp_bucket_name  = 'temp-bucket-' + random_uuid_short()
        cls.versioning        = True
        cls.region_name       = aws_config.region_name() or "eu-east-1"         #todo: see why we need to default to eu-east-1 in GH actions
        cls.s3                = S3()
        assert cls.s3.bucket_create(cls.temp_bucket_name, region=cls.region_name).get('status') is 'ok'
        assert cls.s3.bucket_exists(cls.temp_bucket_name)                                       is True

    @classmethod
    def tearDownClass(cls):
        assert cls.local_stack.is_local_stack_configured_and_available() is True
        assert cls.s3.bucket_delete_all_files(cls.temp_bucket_name) is True
        assert cls.s3.bucket_delete          (cls.temp_bucket_name) is True
        cls.random_aws_creds.restore_vars()
        cls.local_stack.deactivate()