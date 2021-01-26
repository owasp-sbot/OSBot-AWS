import importlib
import sys
from pprint import pprint
from unittest import TestCase

from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.IAM import IAM
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Folder_With_Lambda_File import Temp_Folder_With_Lambda_File
from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_utils.utils.Files import folder_exists, parent_folder, file_contents, file_create, path_combine, \
    folder_create, folder_files, file_name, file_copy, file_delete


#from function_hello_world.aws.deploy.Deploy import Deploy
#from function_hello_world.aws.lambdas.hello_world import run


class test_Deploy_Lambda(TestCase):
    lambda_name = None
    lambda_code = None
    code_folder = None

    @staticmethod
    def setup_test_enviroment__Deploy_Lambda(cls):  # todo: refactor into separate class
        Test_Helper().check_aws_token()
        cls.lambda_name    =  "osbot_test_deploy_lambda"
        cls.lambda_code  = Temp_Folder_With_Lambda_File(cls.lambda_name)
        cls.code_folder  = cls.lambda_code.folder

        lambda_file      = cls.lambda_code.tmp_file
        module_folder    = path_combine(cls.code_folder, "osbot_test_deploy_lambda")
        lambda_in_module = path_combine(module_folder, file_name(lambda_file))
        folder_create(module_folder)
        file_copy(lambda_file, lambda_in_module)        # todo add a file_move to OSBot_Utils
        file_delete(lambda_file)
        file_create(path_combine(module_folder, '__init__.py'), "")

        sys.path.append(cls.code_folder)

        cls.lambda_module   = importlib.import_module("osbot_test_deploy_lambda.osbot_test_deploy_lambda")
        cls.lambda_function = cls.lambda_module.run

    @staticmethod
    def teardown_test_enviroment__Deploy_Lambda(cls):
        sys.path.remove(cls.code_folder)
        pass

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_test_enviroment__Deploy_Lambda(cls)

    @classmethod
    def tearDownClass(cls):
        cls.teardown_test_enviroment__Deploy_Lambda(cls)



    def setUp(self) -> None:
        self.deploy = Deploy_Lambda(self.lambda_function)
        self.aws_config = AWS_Config()
        # Test_Helper().check_aws_token()
        pass

    def tearDown(self):
        self.deploy.delete()


    def test_check_aws_role(self):
        assert Temp_Aws_Roles().for_lambda_invocation_exists()

    def test_get_package(self):
        package = self.deploy.get_package()
        assert package.lambda_name == 'osbot_test_deploy_lambda.osbot_test_deploy_lambda'
        assert package.s3_bucket   == self.aws_config.lambda_s3_bucket()
        assert package.s3_key      == f'{self.aws_config.lambda_s3_key_prefix()}/{package.lambda_name}.zip'
        assert package.role_arn    == f"arn:aws:iam::{self.aws_config.aws_session_account_id()}:role/temp_role_for_lambda_invocation"
        assert folder_exists(package.tmp_folder)

    def test_update(self):
        deploy = Deploy_Lambda(self.lambda_function)
        result = deploy.update()

        assert result['status' ] == 'ok'
        assert result['name']    == self.deploy.lambda_name().replace('.',"_")

        assert result['data']['FunctionArn'] == f'arn:aws:lambda:eu-west-1:{self.aws_config.aws_session_account_id()}:function:osbot_test_deploy_lambda_osbot_test_deploy_lambda'
        assert result['data']['FunctionName'] == 'osbot_test_deploy_lambda_osbot_test_deploy_lambda'
        assert result['data']['Handler'     ] == 'osbot_test_deploy_lambda.osbot_test_deploy_lambda.run'
        assert result['data']['MemorySize'  ] == 3008
        assert result['data']['PackageType' ] == 'Zip'

        assert deploy.invoke()  == 'hello None'
        assert deploy.invoke({"name": "world"}) == "hello world"

        print(deploy.delete())

    def test_invoke(self):
        self.deploy.update()

        assert self.deploy.invoke({"name": "world"}) == "hello world"

        #invoke directly
        aws_lambda = Lambda(name=self.deploy.lambda_name())
        assert aws_lambda.invoke()                  == 'hello None'
        assert aws_lambda.invoke({'name': 'world'}) == 'hello world'

