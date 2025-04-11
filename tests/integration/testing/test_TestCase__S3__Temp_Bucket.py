from osbot_aws.testing.TestCase__S3__Temp_Bucket import TestCase__S3__Temp_Bucket


class test_TestCase__S3__Temp_S3_Bucket(TestCase__S3__Temp_Bucket):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        assert cls.s3.bucket_exists(cls.temp_bucket_name)    is False

    def test__setUpClass(self):
        assert self.local_stack.is_local_stack_configured_and_available() is True
        assert self.s3.bucket_exists(self.temp_bucket_name)               is True


