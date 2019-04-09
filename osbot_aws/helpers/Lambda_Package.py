from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Folder_Code


class Lambda_Package:
    def __init__(self,lambda_name):
        self.lambda_name   = lambda_name
        self._lambda       = Lambda(self.lambda_name)
        self.tmp_s3_bucket = 'gs-lambda-tests'
        self.tmp_s3_key    = 'unit_tests/lambdas/{0}.zip'.format(self.lambda_name)
        self.role_arn      = Temp_Aws_Roles().for_lambda_invocation()
        (self._lambda.set_s3_bucket(self.tmp_s3_bucket)
                     .set_s3_key   (self.tmp_s3_key   )
                     .set_role     (self.role_arn    ))

    def create(self):
        return self._lambda.create()

    def delete(self):
        return self._lambda.delete()

    def use_temp_folder_code(self):
        tmp_folder = Temp_Folder_Code(self.lambda_name)
        self._lambda.set_folder_code(tmp_folder.folder)
        return tmp_folder