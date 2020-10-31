from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.test_helpers.Temp_Lambda import Temp_Lambda

class test_Temp_Lambda(Test_Helper):

    def setUp(self):
        super().setUp()

    def test_simple_execution(self):
        with Temp_Lambda() as _:
            assert 'temp_lambda_' in _.aws_lambda.name
            assert _.invoke({'name':'world'}) == 'hello world'
