from osbot_aws.testing.TestCase__S3__Temp_Bucket import TestCase__S3__Temp_Bucket
from osbot_utils.utils.Dev                       import pprint


class test_S3__bucket_versioning(TestCase__S3__Temp_Bucket):

    def test_bucket_versioning(self):
        assert self.temp_bucket_name.startswith('temp-bucket-')