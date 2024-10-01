from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.aws.lambda_.Lambda                               import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles                 import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Folder_With_Lambda_File   import Temp_Folder_With_Lambda_File
from osbot_utils.utils.Misc                                     import random_string_and_numbers


class Temp_Lambda:
    def __init__(self, lambda_name=None, lambda_code=None, with_layer=None, delete_on_exit=True):
        self.aws_config        = AWS_Config()
        self.lambda_name       = lambda_name or "temp_lambda_{0}".format(random_string_and_numbers())
        self.aws_lambda        = Lambda(self.lambda_name)
        self.tmp_folder        = Temp_Folder_With_Lambda_File(file_name=self.lambda_name, lambda_code=lambda_code).create_temp_file()
        self.role_arn          = Temp_Aws_Roles().for_lambda_invocation__role_arn() # todo: refactor to have option to create the role programatically (needs feature to wait for role to be available)
        self.create_log        = None
        self.delete_on_exit    = delete_on_exit
        self.wait_max_attempts = 40
        self.s3_bucket         = self.aws_config.lambda_s3_bucket()
        self.s3_key            = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.s3                = self.aws_lambda.s3()
        self.with_layer        = with_layer



    def __enter__(self):
        self.create()
        return self

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            self.delete()

    def arn(self):
        return self.aws_lambda.function_arn()

    def create(self):
        (self.aws_lambda.add_layer      (self.with_layer        )
                        .set_role       (self.role_arn          )
                        .set_s3_bucket  (self.s3_bucket         )
                        .set_s3_key     (self.s3_key            )
                        .set_folder_code(self.tmp_folder.folder )
                        .upload())
        self.create_log = self.aws_lambda.create()
        assert self.create_log.get('status') != 'error'
        update_status   =  self.aws_lambda.wait_for_function_update_to_complete(max_attempts=self.wait_max_attempts)
        assert self.exists() is True
        assert update_status == 'Successful'
        return self.create_log

    def delete(self):
        assert self.aws_lambda.delete()
        self.delete_s3_file()

    def exists(self):
        return self.aws_lambda.exists()

    def info(self):
        return self.aws_lambda.info()

    def invoke(self, params=None):
        return self.aws_lambda.invoke(params)

    def invoke_return_logs(self, params=None):
        return self.aws_lambda.invoke_return_logs(params)

    def invoke_raw(self, params=None):
        return self.aws_lambda.invoke_raw(params)

    def set_s3_bucket(self, value):
        self.s3_bucket = value

    def s3_file_exists(self):
        return self.s3.file_exists(self.s3_bucket, self.s3_key)

    def delete_s3_file(self):
        self.s3.file_delete(self.s3_bucket, self.s3_key)
        assert self.s3_file_exists() is False
