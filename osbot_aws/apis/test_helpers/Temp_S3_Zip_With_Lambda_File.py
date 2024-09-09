from osbot_utils.utils.Dev import pprint

from osbot_aws.AWS_Config       import AWS_Config
from osbot_utils.utils.Files    import Files, file_create, path_combine, folder_create_temp, file_delete, folder_delete_recursively
from osbot_utils.utils.Misc     import random_string_and_numbers
from osbot_aws.aws.s3.S3        import S3
from osbot_utils.utils.Zip      import zip_folder


class Temp_S3_Zip_With_Lambda_File:
    def __init__(self, file_name=None,s3_bucket=None, s3_prefix=None, lambda_code=None, create_s3_file=True):
        self.aws_config     = AWS_Config()
        self.s3             = S3()
        self.create_s3_file = create_s3_file
        self.file_name      = file_name or f"temp_zip_file_{random_string_and_numbers()}"
        self.s3_bucket      = s3_bucket or self.aws_config.lambda_s3_bucket()
        self.s3_prefix      = s3_prefix or f'{AWS_Config().lambda_s3_folder_lambdas()}/unit_tests/temp_zips'
        self.s3_key         = f'{self.s3_prefix}/{self.file_name}.zip'
        self.s3_upload_ok   = False
        self.file_delete_ok = False
        self.lambda_code    = lambda_code or "def run(event, context): return 'from Temp_S3_Zip_With_Lambda_File, hello {0}'.format(event.get('name'))" # todo: use function_source_code(run)
        self.folder_temp    = None
        self.file_temp      = None
        self.file_zip       = None

    def __enter__(self):
        self.create_temp_file()
        self.s3_file_create()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete_local_files()
        self.s3_file_delete()

#    def create_s3_file(self, new_code = None):
#

    def create_temp_file(self):
        self.folder_temp = folder_create_temp('tmp_lambda_')
        self.file_temp    = path_combine(self.folder_temp, f'{self.file_name}.py')
        file_create(self.file_temp, self.lambda_code)
        return self

    def delete_local_files(self):
        file_delete(self.file_zip)
        folder_delete_recursively(self.folder_temp)

    def s3_bucket_exists(self):
        return self.s3.bucket_exists(self.s3_bucket)

    def s3_file_create(self):
        temp_zip_file = self.zip()
        self.s3_upload_ok = self.s3.file_upload_to_key(temp_zip_file, self.s3_bucket, self.s3_key)

    def s3_file_delete(self):
        self.file_delete_ok = self.s3.file_delete(self.s3_bucket, self.s3_key)

    def s3_file_exists(self):
        return self.s3.file_exists(self.s3_bucket, self.s3_key)

    # def s3_file_contents(self):
    #     from gzip import GzipFile
    #     bytes = self.s3.file_bytes(self.s3_bucket, self.s3_key)
    #     return GzipFile(None, 'rb', fileobj=bytes)

    def s3_files_in_folder(self):
        return self.s3.find_files(self.s3_bucket, self.s3_prefix)

    def zip(self):
        self.file_zip = zip_folder(self.folder_temp)
        return self.file_zip

    def zip_bytes(self):
        with open(self.zip(), 'rb') as file_data:
            return file_data.read()