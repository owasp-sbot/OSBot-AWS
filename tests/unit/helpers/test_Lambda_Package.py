import sys ;

import pytest
from osbot_utils.utils.Files import Files, file_name

sys.path.append('..')
from unittest import TestCase

from osbot_utils.utils import Misc
from osbot_aws.helpers.Lambda_Package import Lambda_Package


class test_Lambda_Package(TestCase):
    def setUp(self):
        self.lambda_name   = "temp_lambda_{0}".format(Misc.random_string_and_numbers())
        self.package = Lambda_Package(self.lambda_name)

    def tearDown(self):
        if self.package.aws_lambda.exists():
            self.package.delete()
            assert self.package.aws_lambda.exists() is False

    def test__init__(self):
        assert type(self.package.aws_lambda).__name__ == 'Lambda'

    def test_add_file(self):
        lambda_file = Files.path_combine(__file__,'../../../../osbot_aws/lambdas/dev/hello_world.py')
        assert Files.exists(lambda_file)
        self.package.add_file(lambda_file)
        assert self.package.get_files() == ['/hello_world.py']
        self.package.aws_lambda.handler = 'hello_world.run'
        self.package.update()
        assert self.package.invoke() == 'From lambda code, hello None'

    @pytest.mark.skip('Fix tests') #todo: error below is caused by lack of dotenv in lambda package
    def test_add_folder(self):
        self.package.add_folder(self.package.get_root_folder())
        self.package.aws_lambda.handler= 'osbot_aws.lambdas.dev.check_aws_api.run'
        self.package.update()
        assert self.package.invoke() == "checking aws api: <class 'osbot_aws.Globals.Globals'>"

    def test_add_osbot_utils(self):
        self.package.add_root_folder()
        self.package.add_osbot_utils()
        assert len(self.package.get_files()) > 10
        self.package.aws_lambda.handler = 'osbot_aws.lambdas.dev.check_python_utils.run'
        self.package.update()
        assert 'checking python utils: /tmp' in self.package.invoke()


    def test_get_root_folder(self):
        assert self.package.get_root_folder().endswith('osbot_aws') is True

    def test_use_lambda_file(self):
        assert self.package.use_lambda_file('lambdas/dev/hello_world.py').get('status') == 'ok'

        files = self.package.get_files()
        assert len(files) == 1
        assert file_name(files.pop()) == '{0}.py'.format(self.package.lambda_name)

        assert self.package.update().get('status') == 'ok'
        assert self.package.invoke({'name':'world'}) == 'From lambda code, hello world'


    def test_use_lambda_file__bad_file(self):
        result = self.package.use_lambda_file('lambdas/dev/aaaaaaa')
        assert result.get('status') == 'error'
        assert 'could not find lambda file `lambdas/dev/aaaaaaa`' in result.get('data')


    def test_update_with_root_folder(self):
        name = 'osbot_aws.lambdas.dev.check_python_utils'
        assert 'checking python utils: /tmp' in Lambda_Package(name).update_with_root_folder().invoke()