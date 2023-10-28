from osbot_utils.utils.Files     import Files, file_write, file_exists
from osbot_utils.utils.Functions import function_source_code
from osbot_utils.utils.Zip import folder_zip


class Temp_Folder_With_Lambda_File:
    def __init__(self, file_name=None, lambda_code=None):
        self.file_name    = file_name or 'simple_lambda.py'
        self.folder       = None
        self.lambda_code  = lambda_code or "def run(event, context): print('OSBot inside an Lambda :)'); return 'hello {0}'.format(event.get('name'))"
        self.tmp_file     = None
        self.create_temp_file()

    def __enter__(self):
        return self.create_temp_file()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.delete()

    def create_temp_file(self, new_code=None):
        self.folder      = Files.temp_folder('tmp_lambda_')
        self.lambda_code = new_code or function_source_code(self.lambda_code)                   # extracts source code if self.lambda_code is a function
        self.tmp_file    = Files.path_combine(self.folder, '{0}.py'.format(self.file_name))
        file_write(self.tmp_file, self.lambda_code)
        assert file_exists(self.tmp_file)
        return self

    def delete(self):
        return Files.folder_delete_all(self.folder)

    def zip(self):
        return folder_zip(self.folder)

    def zip_bytes(self):
        with open(self.zip(), 'rb') as file_data:
            return file_data.read()