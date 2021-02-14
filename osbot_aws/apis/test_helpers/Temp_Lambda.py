from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.Lambda                        import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles   import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Folder_With_Lambda_File import Temp_Folder_With_Lambda_File
from osbot_utils.utils.Misc import random_string_and_numbers


class Temp_Lambda:
    def __init__(self, lambda_name=None):
        self.lambda_name    = lambda_name or "temp_lambda_{0}".format(random_string_and_numbers())
        self.aws_lambda     = Lambda(self.lambda_name)
        self.tmp_folder     = Temp_Folder_With_Lambda_File(self.lambda_name).create_temp_file()
        self.role_arn       = Temp_Aws_Roles().for_lambda_invocation__role_arn() # todo: refactor to have option to create the role programatically (needs feature to wait for role to be available)
        self.create_log     = None
        self.delete_on_exit = True
        self.s3_bucket      = AWS_Config().lambda_s3_bucket()
        self.s3_key         = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.s3             = self.aws_lambda.s3()


    def __enter__(self):
        self.create()
        return self

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            self.delete()

    def arn(self):
        return self.aws_lambda.function_Arn()

    def create(self):
        (self.aws_lambda.set_role       (self.role_arn)
                        .set_s3_bucket  (self.s3_bucket         )
                        .set_s3_key     (self.s3_key            )
                        .set_folder_code(self.tmp_folder.folder )
                        .upload())
        self.create_log = self.aws_lambda.create()
        assert self.exists() is True
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

    def invoke_raw(self, params=None):
        return self.aws_lambda.invoke_raw(params)

    def set_s3_bucket(self, value):
        self.s3_bucket = value

    def s3_file_exists(self):
        return self.s3.file_exists(self.s3_bucket, self.s3_key)

    def delete_s3_file(self):
        self.s3.file_delete(self.s3_bucket, self.s3_key)
        assert self.s3_file_exists() is False
