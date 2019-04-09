from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Folder_Code
from osbot_aws.helpers.Lambda_Package import Lambda_Package


class test_Lambda_Package(TestCase):
    def setUp(self):
        self.lambda_name   = "temp_lambda_{0}".format(Misc.random_string_and_numbers())
        self.package = Lambda_Package(self.lambda_name)

    def tearDown(self):
        if self.package._lambda.exists():
            self.package.delete()
            assert self.package._lambda.exists() is False

    def test__init__(self):
        assert type(self.package._lambda).__name__ == 'Lambda'

    def test_get_root_folder(self):
        assert self.package.get_root_folder().endswith('osbot_aws') is True

    def test_use_temp_folder_code(self):
        self.package.use_temp_folder_code()
        assert self.package.update().get('status') == 'ok'
        assert self.package.invoke() == 'hello None'

    def test_use_lambda_file(self):
        assert self.package.use_lambda_file('lambdas/dev/hello_world.py').get('status') == 'ok'
        assert self.package.update().get('status') == 'ok'
        assert self.package.invoke({'name':'world'}) == 'From lambda code, hello world'


    def test_use_lambda_file__bad_file(self):
        result = self.package.use_lambda_file('lambdas/dev/aaaaaaa')
        assert result.get('status') == 'error'
        assert 'could not find lambda file `lambdas/dev/aaaaaaa`' in result.get('data')