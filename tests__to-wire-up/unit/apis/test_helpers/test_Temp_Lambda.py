import pytest

from osbot_aws.apis.test_helpers.Temp_Aws_Roles import Temp_Aws_Roles
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda

class test_Temp_Lambda(Test_Helper):

    @staticmethod
    def setup_test_enviroment():            # todo: refactor into separate class
        print()
        temp_aws_roles =  Temp_Aws_Roles()
        if temp_aws_roles.for_lambda_invocation__not_exists():
            temp_aws_roles.for_lambda_invocation__create()

    @classmethod
    def setUpClass(cls) -> None:
        cls.setup_test_enviroment()

    def setUp(self):
        super().setUp()

    def test_simple_execution(self):
        with Temp_Lambda() as _:
            assert 'temp_lambda_' in _.aws_lambda.name
            assert _.invoke({'name':'world'}) == 'hello world'
