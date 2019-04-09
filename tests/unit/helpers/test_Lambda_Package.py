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

    def test_with_temp_folder(self):
        self.tmp_folder = Temp_Folder_Code(self.lambda_name)
        self.package._lambda.set_folder_code(self.tmp_folder.folder )
        self.package._lambda.upload()
        self.package.create()
        assert self.package._lambda.exists() is True

        Dev.pprint(self.package._lambda.invoke())