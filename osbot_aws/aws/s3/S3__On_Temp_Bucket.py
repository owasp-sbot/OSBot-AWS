from osbot_aws.AWS_Config               import AWS_Config
from osbot_aws.aws.s3.S3                import S3
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Files import is_file

FORMAT__TEMP_BUCKET_NAME = S3_TEMP_BUCK = '{account_id}--osbot--temp--{region_name}'

class S3__On_Temp_Bucket(Type_Safe):
    aws_config: AWS_Config
    s3        : S3

    def add_file(self, path_to_file, s3_key=None):
        return self.s3.file_upload_to_key(file=path_to_file, bucket=self.bucket_name(), key=s3_key)

    def create_file__from_string(self, s3_key, file_contents):
            return self.s3.file_create_from_string(bucket=self.bucket_name(), key=s3_key, file_contents=file_contents)

    def create_file__from_bytes(self, s3_key, file_bytes):
        return self.s3.file_create_from_bytes(bucket=self.bucket_name(), key=s3_key, file_bytes=file_bytes)

    def bucket_exists(self):
        return self.s3.bucket_exists(self.bucket_name())

    def bucket_name(self):
        account_id = self.aws_config.account_id()
        region_name = self.aws_config.region_name()
        return FORMAT__TEMP_BUCKET_NAME.format(account_id=account_id, region_name=region_name)

    def file_contents(self, s3_key):
        return self.s3.file_contents(self.bucket_name(), s3_key)

    def file_delete(self, s3_key):
        return self.s3.file_delete(self.bucket_name(), s3_key)

    def file_exists(self, s3_key):
        return self.s3.file_exists(self.bucket_name(), s3_key)
