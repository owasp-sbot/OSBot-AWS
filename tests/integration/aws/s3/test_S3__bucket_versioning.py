from osbot_aws.testing.TestCase__S3__Temp_Bucket import TestCase__S3__Temp_Bucket


class test_S3__bucket_versioning(TestCase__S3__Temp_Bucket):

    def test__bucket_versioning(self):
        bucket_name = self.temp_bucket_name
        with self.s3 as _:
            assert _.bucket_versioning__status(bucket_name) == 'Not Enabled'
            assert _.bucket_versioning__enable(bucket_name) is True
            assert _.bucket_versioning__status(bucket_name) == 'Enabled'

    def test__file_versions(self):
        bucket_name = self.temp_bucket_name
        with self.s3 as _:
            assert _.bucket_versioning__enable(bucket_name) is True



