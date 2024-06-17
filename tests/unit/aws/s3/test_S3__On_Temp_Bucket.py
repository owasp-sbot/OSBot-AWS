from osbot_aws.aws.boto3.Cache_Boto3_Requests import Cache_Boto3_Requests
from osbot_aws.aws.s3.S3__On_Temp_Bucket import S3__On_Temp_Bucket
from osbot_aws.testing.TestCase__Boto3_Cache import TestCase__Boto3_Cache
from osbot_aws.testing.TestCase__S3 import TestCase__S3
from osbot_utils.decorators.methods.capture_exception import capture_exception
from osbot_utils.utils.Dev import pprint


class test_S3__On_Temp_Bucket(TestCase__S3):

    def setUp(self):
        self.s3_on_temp = S3__On_Temp_Bucket(s3=self.s3)
        self.aws_config = self.s3_on_temp.aws_config

    def test_bucket_name(self):
        assert self.s3_on_temp.bucket_name() == f'{self.aws_config.account_id()}--osbot--temp--{self.aws_config.region_name()}'

    def test_bucket_exists(self):
        assert self.s3_on_temp.bucket_exists() is True

    def test_create_file__from_string(self):
        self.cache.disable()                                    # todo: figure out why the file contents doesn't cache ok
        key           = 'test.txt'
        file_contents = 'hello world'
        with self.s3_on_temp as _:
            assert _.create_file__from_string(key, file_contents) is True
            assert _.file_exists  (key) is True
            assert _.file_contents(key)  == 'hello world'
            assert _.file_delete  (key) is True


        #assert self.s3_on_temp.get_file(key) == data
