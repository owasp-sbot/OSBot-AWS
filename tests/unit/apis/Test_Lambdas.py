import os
import unittest

from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.Lambdas import Lambdas
from osbot_aws.helpers.IAM_Role import IAM_Role

lambda_name   = 'tmp_lambda_dev_test'
tmp_s3_bucket = 'gs-lambda-tests'
tmp_s3_key    =  'unit_tests/lambdas/s{0}.zip'.format(lambda_name)

class Test_Lambdas(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        lambdas = Lambdas(lambda_name)

    @classmethod
    def tearDownClass(cls):
        lambdas = Lambdas(lambda_name)

    def setUp(self):
        self.lambdas = Lambdas(lambda_name)

    def test__init__(self):
        assert self.lambdas.runtime       == 'python3.6'
        assert self.lambdas.memory        == 3008
        assert self.lambdas.timeout       == 60
        assert self.lambdas.original_name == lambda_name

    def test_create_function__no_params(self):
        assert self.lambdas.create_function() == { 'error': "missing fields in create_function: ['role', 's3_bucket', 's3_key']"}

    def test_create_function(self):
        temp_role = IAM_Role(lambda_name + '__tmp_role').create_for_lambda()
        Dev.pprint(temp_role)
        (
                self.lambdas.set_role      (temp_role.get('role_arn'))
                            .set_s3_bucket (tmp_s3_bucket)
                            .set_s3_key    (tmp_s3_key)
        )

        Dev.pprint(self.lambdas.create_function())

    # def test_constructor(self):
    #     assert self.test_lambda.role      == 'arn:aws:iam::244560807427:role/lambda_with_s3_access'
    #     assert self.test_lambda.s3_bucket == 'gs-lambda-tests'
    #     assert self.test_lambda.name      == self.name
    #     assert self.test_lambda.handler   == self.handler
    #     assert self.test_lambda.s3_key    == 'dinis/lambdas/{0}.zip'.format(self.name)
    #
    #     assert os.path.exists(self.test_lambda.source) is True



    # def test_upload_update(self):
    #     assert self.test_lambda.delete() == self.test_lambda
    #     assert self.test_lambda.exists() is False
    #     assert self.test_lambda.update() == self.test_lambda               # first update will  update s3 bucket and create function
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.update() == self.test_lambda               # 2nd update will just update s3 bucket and call the update function method
    #     assert self.test_lambda.invoke() == "hello None"
    #     assert self.test_lambda.delete() == self.test_lambda