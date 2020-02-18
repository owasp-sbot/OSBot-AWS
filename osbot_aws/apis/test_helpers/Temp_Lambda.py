from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.Globals                            import Globals
from osbot_aws.apis.Lambda                        import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles   import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Folder_Code import Temp_Folder_Code


class Temp_Lambda:
    def __init__(self):
        self.lambda_name    = "temp_lambda_{0}".format(Misc.random_string_and_numbers())
        self.aws_lambda     = Lambda(self.lambda_name)
        self.tmp_folder     = Temp_Folder_Code(self.lambda_name)
        self.role_arn       = Temp_Aws_Roles().for_lambda_invocation()
        self.create_log     = None
        self.delete_on_exit = True
        self.s3_bucket      = Globals.lambda_s3_bucket
        self.s3_key         = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.s3             = self.aws_lambda.s3()


    def __enter__(self):
        (
            self.aws_lambda.set_role       (self.role_arn)
                            .set_s3_bucket  (self.s3_bucket          )
                            .set_s3_key     (self.s3_key             )
                            .set_folder_code(self.tmp_folder.folder )
        )
        self.aws_lambda.upload()
        self.create_log = self.aws_lambda.create()
        assert self.aws_lambda.exists() == True
        return self

    def __exit__(self, type, value, traceback):
        if self.delete_on_exit:
            assert self.aws_lambda.delete() is True
            self.delete_s3_file()

    def arn(self):
        return self.aws_lambda.function_Arn()

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
        return self
