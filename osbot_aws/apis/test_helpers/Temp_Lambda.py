from time import sleep

from pbx_gs_python_utils.utils.Files import Files
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.Globals import Globals
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.S3 import S3
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.helpers.IAM_Role import IAM_Role


class Temp_Lambda:
    def __init__(self):
        self.name           = "temp_lambda_{0}".format(Misc.random_string_and_numbers())
        self.temp_lambda    = Lambda(self.name)
        self.tmp_folder     = Temp_Folder_Code(self.name)
        self.role_arn       = Temp_Aws_Roles().for_lambda_invocation()
        self.create_log     = None
        self.delete_on_exit = True
        self.lambda_name    = 'tmp_lambda_dev_test'
        self.s3_bucket      = Globals.lambda_s3_bucket
        self.s3_key         =  'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)


    def __enter__(self):
        (
            self.temp_lambda.set_role       (self.role_arn)
                            .set_s3_bucket  (self.s3_bucket          )
                            .set_s3_key     (self.s3_key             )
                            .set_folder_code(self.tmp_folder.folder )
        )
        self.temp_lambda.upload()
        self.create_log = self.temp_lambda.create()
        assert self.temp_lambda.exists() == True
        return self

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            assert self.temp_lambda.delete() is True

    def invoke(self, params=None):
        return self.temp_lambda.invoke(params)

    def invoke_raw(self, params=None):
        return self.temp_lambda.invoke_raw(params)

    def set_s3_bucket(self, value):
        self.s3_bucket = value

class Temp_Folder_Code:
    def __init__(self, file_name):
        self.file_name    = file_name
        self.s3           = S3()
        self.folder       = Files.temp_folder('tmp_lambda_')
        self.lambda_code  = "def run(event, context): return 'hello {0}'.format(event.get('name'))"
        self.tmp_file     = None
        self.s3_bucket    = Globals.lambda_s3_bucket
        self.lambda_name  = 'tmp_lambda_dev_test'
        self.s3_key       = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.create_temp_file()

    def create_temp_file(self, new_code=None):
        if new_code: self.lambda_code = new_code
        self.tmp_file = Files.path_combine(self.folder, '{0}.py'.format(self.file_name))
        Files.write(self.tmp_file, self.lambda_code)
        assert Files.exists(self.tmp_file)
        return self

    def s3_file_exists(self):
        return self.s3.file_exists(self.s3_bucket, self.s3_key)

    def delete_s3_file(self):
        self.s3.file_delete(self.s3_bucket, self.s3_key)
        assert self.s3_file_exists() is False
        return self
