from osbot_aws.aws.s3.S3                    import S3
from osbot_utils.utils.Misc                 import random_string_and_numbers
from osbot_aws.AWS_Config                   import AWS_Config
from osbot_utils.testing.Temp_Zip_In_Memory import Temp_Zip_In_Memory


class S3_Zip_From_Files(Temp_Zip_In_Memory):

    def __init__(self, file_name=None, s3_bucket=None, s3_prefix=None):
        super().__init__()
        self.aws_config     = AWS_Config()
        self.s3             = S3()
        self.file_name      = file_name or f"temp_zip_file_{random_string_and_numbers()}"
        self.s3_bucket      = s3_bucket or self.aws_config.lambda_s3_bucket()
        self.s3_prefix      = s3_prefix or f'{AWS_Config().lambda_s3_folder_lambdas()}/unit_tests/temp_zips'
        self.s3_key         = f'{self.s3_prefix}/{self.file_name}.zip'

    def __enter__(self):
        super().__enter__()
        return self

    def __exit__(self, type, value, traceback):
        super().__exit__(type, value, traceback)
        pass

    def s3_file_create(self):
        kwargs = dict(file_body = self.zip_bytes(),
                      bucket    = self.s3_bucket  ,
                      key       = self.s3_key     )
        return self.s3.file_upload_from_bytes(**kwargs)

    def s3_file_delete(self):
        return self.s3.file_delete(self.s3_bucket, self.s3_key)

    def s3_file_exists(self):
        return self.s3.file_exists(self.s3_bucket, self.s3_key)

    def s3_file_contents(self):
        return self.s3.file_bytes(self.s3_bucket, self.s3_key)