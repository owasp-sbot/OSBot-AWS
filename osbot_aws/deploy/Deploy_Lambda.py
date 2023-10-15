from dotenv import load_dotenv
from osbot_utils.testing.Duration import Duration

from osbot_aws.helpers.Lambda_Layer_Create import Lambda_Layer_Create
from osbot_utils.utils.Misc import wait_for

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
        # self.layers               = []
        # self.env_variables        = {}
        self.package              = self.get_package()

    def add_function_source_code(self):
        root_module_name = self.handler.__module__.split(".").pop(0)
        self.package.add_module(root_module_name)

    def add_module(self, module_name):
        self.package.add_module(module_name)
        return self

    def add_osbot_aws    (self):    self.package.add_osbot_aws    () ; return self
    def add_osbot_browser(self):    self.package.add_osbot_browser() ; return self
    def add_osbot_utils  (self):    self.package.add_osbot_utils  () ; return self
    def add_osbot_elastic(self):    self.package.add_osbot_elastic() ; return self

    def delete(self):
        return self.lambda_function().delete()

    def deploy(self):
        return self.update() == 'Successful'

    def exists(self):
        return self.package.aws_lambda.exists()

    def invoke(self, params=None):
        return self.lambda_function().invoke(params)

    def invoke_async(self, params=None):
        return self.lambda_function().invoke_async(params)

    def files(self):
        return self.package.get_files()

    def get_package(self):
        package = Lambda_Package(self.module_name)
        package.aws_lambda.set_s3_bucket(self.osbot_setup.s3_bucket_lambdas)
        package.aws_lambda.set_role(self.role_arn)
        return package

    def lambda_name(self):
        return self.package.lambda_name

    def lambda_function(self):
        return self.package.aws_lambda



    def update(self, wait_for_update=True):
        self.add_function_source_code()
        if len(self.package.get_files()) == 0:                       # todo: add this check to the package.update()  method
            raise Exception("There are not files to deploy")
        update_result= self.package.update()
        if update_result.get('status') == 'ok':
            if wait_for_update:
                return self.lambda_function().wait_for_function_update_to_complete()
        return update_result

    def set_container_image(self, image_uri):
        self.package.set_image_uri(image_uri)

    def set_layers(self, layers):
        self.package.set_layers(layers)

    def set_packages_using_layer(self, packages, skip_layer_creation_if_exists=True):
        layer_name          = f'layer_for__{self.lambda_name()}'
        lambda_layer_create = Lambda_Layer_Create(layer_name)
        lambda_layer_create.add_packages(packages)
        layer_arn           = lambda_layer_create.create(skip_if_exists=skip_layer_creation_if_exists)
        self.lambda_function().add_layer(layer_arn)
        return lambda_layer_create
    def set_env_variables(self, env_variables):
        self.package.set_env_variables(env_variables)


# legacy methods
Deploy_Lambda.lambda_invoke = Deploy_Lambda.invoke
