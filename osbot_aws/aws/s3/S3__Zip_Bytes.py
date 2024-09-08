from osbot_aws.aws.s3.S3           import S3
from osbot_utils.helpers.Zip_Bytes import Zip_Bytes


class S3__Zip_Bytes(Zip_Bytes):
    s3: S3

    def save_to_s3(self, s3_bucket, s3_key):
        kwargs = dict(file_bytes = self.zip_bytes,
                      bucket     = s3_bucket     ,
                      key        = s3_key        )
        return self.s3.file_create_from_bytes(**kwargs)
