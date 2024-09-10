from unittest import TestCase

from osbot_aws.aws.s3.S3        import S3
from osbot_aws.aws.s3.S3__Minio import S3__Minio, DEFAULT__MINIO__SERVER


class test__regression__S3(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.s3_minio  = S3__Minio()

    def test__regression__failed_to_connect_to_s3_with_minio_endpoint(self):
        server, aws_access_key_id, aws_secret_access_key = self.s3_minio.connection_details()

        kwargs = dict(endpoint_url=server, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        s3 = S3(**kwargs)

        assert s3.endpoint_url          == DEFAULT__MINIO__SERVER
        assert s3.aws_secret_access_key == aws_secret_access_key
        assert s3.aws_access_key_id     == aws_access_key_id
        assert type(s3.buckets()) is list                       # BUG: FIXED: was trowing an exception here
