from osbot_aws.Globals       import Globals
from osbot_utils.utils.Files import Files, file_create, path_combine, folder_create_temp
from osbot_utils.utils.Misc  import random_string_and_numbers

from osbot_aws.apis.S3 import S3

class Temp_S3_Zip_With_Lambda_File:
    def __init__(self, file_name=None,s3_bucket=None, s3_prefix=None):
        self.file_name    = file_name or f"temp_zip_file_{random_string_and_numbers()}"
        self.s3_bucket    = Globals.lambda_s3_bucket
        self.s3_prefix    = f'{Globals.lambda_s3_key_prefix}/unit_tests/temp_zips'
        self.s3_key       = f'{self.s3_prefix}/{self.file_name}.zip'
        self.folder       = None
        self.lambda_code  = "def run(event, context): return 'hello {0}'.format(event.get('name'))"
        self.tmp_file     = None
        self.create_temp_file()

    def __enter__(self):
        return self.create_temp_file()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()

#    def create_s3_file(self, new_code = None):
#

    def create_temp_file(self, new_code=None):
        self.lambda_code = new_code or self.lambda_code
        self.folder      = folder_create_temp('tmp_lambda_')
        self.tmp_file    = path_combine(self.folder, f'{self.file_name}.py')
        file_create(self.tmp_file, self.lambda_code)
        return self

    def delete(self):
        return Files.folder_delete_all(self.folder)

    def zip(self):
        return Files.zip_folder(self.folder)

    def zip_bytes(self):
        with open(self.zip(), 'rb') as file_data:
            return file_data.read()