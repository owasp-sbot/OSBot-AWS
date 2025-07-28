from osbot_aws.AWS_Config import AWS_Config

from osbot_aws.aws.s3.S3 import S3

from osbot_utils.type_safe.Type_Safe import Type_Safe


class Lambda__Dependency__S3(Type_Safe):
    s3         : S3
    aws_config : AWS_Config

    def bucket__name(self):
        return self.aws_config.lambda_s3_bucket()

    def bucket__exists(self):
        return self.s3.bucket_exists(self.bucket__name())

    def setup(self):
        bucket_name = self.bucket__name()
        if self.bucket__exists() is False:
            region_name = self.aws_config.region_name()
            self.s3.bucket_create(bucket= bucket_name, region=region_name)
        return self

