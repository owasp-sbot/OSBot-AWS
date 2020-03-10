from osbot_aws.Globals import Globals
from pbx_gs_python_utils.utils.Files import Files

from osbot_aws.apis.S3 import S3

#todo: refactor with better helper methods
class Temp_Folder_With_Lambda_File:
    def __init__(self, file_name):
        self.file_name    = file_name
        self.folder       = None
        self.lambda_code  = "def run(event, context): return 'hello {0}'.format(event.get('name'))"
        self.tmp_file     = None
        self.create_temp_file()

    def __enter__(self):
        return self.create_temp_file()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()

    def create_temp_file(self, new_code=None):
        self.folder = Files.temp_folder('tmp_lambda_')
        if new_code: self.lambda_code = new_code
        self.tmp_file = Files.path_combine(self.folder, '{0}.py'.format(self.file_name))
        Files.write(self.tmp_file, self.lambda_code)
        assert Files.exists(self.tmp_file)
        return self

    def delete(self):
        return Files.folder_delete_all(self.folder)

    def zip(self):
        return Files.zip_folder(self.folder)

    def zip_bytes(self):
        with open(self.zip(), 'rb') as file_data:
            return file_data.read()