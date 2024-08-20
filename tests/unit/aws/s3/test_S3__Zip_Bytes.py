from unittest import TestCase

import boto3

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.s3.S3__On_Temp_Bucket import S3__On_Temp_Bucket
from osbot_aws.aws.s3.S3__Zip_Bytes                     import S3__Zip_Bytes
from osbot_aws.aws.sts.STS import STS
from osbot_aws.testing.TestCase__S3                     import TestCase__S3
from osbot_utils.decorators.methods.capture_exception   import capture_exception
from osbot_utils.utils.Dev                              import pprint
from osbot_utils.utils.Objects import obj_info
from osbot_utils.utils.Zip import zip_bytes__files


class test_S3__Zip_Bytes(TestCase__S3):


    
    def test_save_to_s3(self):
        s3_on_temp_bucket =  S3__On_Temp_Bucket()
        bucket_name       = s3_on_temp_bucket.bucket_name()
        s3_key            = 'test_save_to_s3.zip'
        with S3__Zip_Bytes(s3=self.s3) as _:
            _.add_random_file()
            assert _.size() == 1
            assert _.save_to_s3(bucket_name, s3_key    ) is True

            assert _.s3.file_exists(bucket_name, s3_key) is True
            zip_bytes_from_s3 = _.s3.file_bytes(bucket_name, s3_key)
            assert zip_bytes_from_s3 == _.zip_bytes
            assert zip_bytes__files(zip_bytes_from_s3) == _.files()
            assert _.s3.file_delete(bucket_name, s3_key) is True






