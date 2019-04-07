import os
import unittest

from utils.aws.Lambdas  import Lambdas

class Test_Lambdas(unittest.TestCase):

    def setUp(self):
        self.name      = 'lambda_dev_test'
        self.handler   = 'lambdas.dev.hello_world.run'
        self.test_lambda = Lambdas(self.name, self.handler)

    def test_constructor(self):
        assert self.test_lambda.role      == 'arn:aws:iam::244560807427:role/lambda_with_s3_access'
        assert self.test_lambda.s3_bucket == 'gs-lambda-tests'
        assert self.test_lambda.name      == self.name
        assert self.test_lambda.handler   == self.handler
        assert self.test_lambda.s3_key    == 'dinis/lambdas/{0}.zip'.format(self.name)

        assert os.path.exists(self.test_lambda.source) is True

    def test_create_delete_exists_invoke(self):
        assert self.test_lambda.delete(             ) == self.test_lambda  # delete function
        assert self.test_lambda.exists(             ) is False             # confirm it doesn't exist
        assert self.test_lambda.create(             ) == self.test_lambda  # confirm create returns test_lambda object
        assert self.test_lambda.exists(             ) is True              # confirm it now exists
        assert self.test_lambda.invoke(             ) == "hello None"      # invoke with no params
        assert self.test_lambda.invoke({'name':'AA'}) == "hello AA"        # invoke with an param
        assert self.test_lambda.delete(             ) == self.test_lambda  # delete it
        assert self.test_lambda.exists(             ) is False             # confirm deletion

    def test_upload_update(self):
        assert self.test_lambda.delete() == self.test_lambda
        assert self.test_lambda.exists() is False
        assert self.test_lambda.update() == self.test_lambda               # first update will  update s3 bucket and create function
        assert self.test_lambda.invoke() == "hello None"
        assert self.test_lambda.update() == self.test_lambda               # 2nd update will just update s3 bucket and call the update function method
        assert self.test_lambda.invoke() == "hello None"
        assert self.test_lambda.delete() == self.test_lambda