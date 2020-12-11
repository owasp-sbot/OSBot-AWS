from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.OSBot_Setup import OSBot_Setup
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.helpers.Lambda_Package import Lambda_Package

class Deploy_Lambda:

    def __init__(self, handler):
        self.osbot_setup          = OSBot_Setup()
        self.handler              = handler
        self.lambda_name          = handler.__module__
        self.role_arn             = Temp_Aws_Roles().for_lambda_invocation__role_arn()
        self.package              = self.get_package()

    # todo add these helper methods
    # def check_aws_role(self):
    #     pass        # todo : add custom role for this function
    #
    # def check_aws_bucket(self):
    #     pass
    def lambda_function(self):
        return self.package.aws_lambda

    def lambda_invoke(self, params=None):
        return self.lambda_function().invoke(params)

    def get_package(self):
        package = Lambda_Package(self.lambda_name)
        package.aws_lambda.set_s3_bucket(self.osbot_setup.s3_bucket_lambdas)
        package.aws_lambda.set_role(self.role_arn)
        return package

    def add_function_source_code(self):
        root_module_name = self.handler.__module__.split(".").pop(0)
        self.package.add_module(root_module_name)

    def update(self):
        self.add_function_source_code()
        if len(self.package.get_files()) == 0:                       # todo: add this check to the package.update()  method
            raise Exception("There are not files to deploy")
        return self.package.update()

    def delete(self):
        return self.lambda_function().delete()