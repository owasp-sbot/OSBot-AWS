from dotenv import load_dotenv

from osbot_aws.OSBot_Setup import OSBot_Setup
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.helpers.Lambda_Package import Lambda_Package

class Deploy_Lambda:

    def __init__(self, handler):
        load_dotenv()
        self.osbot_setup          = OSBot_Setup()
        self.handler              = handler
        self.module_name          = handler.__module__
        self.role_arn             = Temp_Aws_Roles().for_lambda_invocation__role_arn()
        self.package              = self.get_package()

    def add_function_source_code(self):
        root_module_name = self.handler.__module__.split(".").pop(0)
        self.package.add_module(root_module_name)

    def add_osbot_aws    (self):    self.package.add_osbot_aws    () ; return self
    def add_osbot_browser(self):    self.package.add_osbot_browser() ; return self
    def add_osbot_utils  (self):    self.package.add_osbot_utils  () ; return self
    def add_osbot_elastic(self):    self.package.add_osbot_elastic() ; return self

    def delete(self):
        return self.lambda_function().delete()

    def deploy(self):
        return self.update().get('status') == 'ok'

    def exists(self):
        return self.package.aws_lambda.exists()

    def invoke(self, params=None):
        return self.lambda_function().invoke(params)

    def invoke_async(self, params=None):
        return self.lambda_function().invoke_async(params)


    def get_package(self):
        package = Lambda_Package(self.module_name)
        package.aws_lambda.set_s3_bucket(self.osbot_setup.s3_bucket_lambdas)
        package.aws_lambda.set_role(self.role_arn)
        return package

    def lambda_name(self):
        return self.package.lambda_name

    def lambda_function(self):
        return self.package.aws_lambda



    def update(self):
        self.add_function_source_code()
        if len(self.package.get_files()) == 0:                       # todo: add this check to the package.update()  method
            raise Exception("There are not files to deploy")
        return self.package.update()

    def set_container_image(self, image_uri):
        self.package.set_image_uri(image_uri)

# legacy methods
Deploy_Lambda.lambda_invoke = Deploy_Lambda.invoke
