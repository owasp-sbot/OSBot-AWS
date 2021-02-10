from unittest                           import TestCase
from osbot_aws.apis.STS                 import STS
from osbot_aws.lambdas.dev.hello_world  import run
from osbot_aws.apis.Lambda              import Lambda
from osbot_aws.deploy.Deploy_Lambda     import Deploy_Lambda

class test_hello_world(TestCase):
    lambda_ : Lambda

    @classmethod
    def setUpClass(cls) -> None:
        STS().check_current_session_credentials()
        cls.handler     = run
        cls.deploy      = Deploy_Lambda(cls.handler)
        cls.lambda_name = cls.deploy.lambda_name()
        cls.lambda_     = Lambda(name= cls.lambda_name)
        assert cls.deploy.deploy() is True
        assert cls.lambda_.exists() is True

    @classmethod
    def tearDownClass(cls) -> None:
        assert cls.lambda_.delete() is True

    def test_invoke_directly(self):
        assert self.handler.__module__ == self.lambda_name
        assert run({}                ) == 'From lambda code, hello None'
        assert run({'name' : 'world'}) == 'From lambda code, hello world'

    def test_invoke_lambda__using_deploy(self):
        assert self.deploy.invoke() == 'From lambda code, hello None'

    def test_invoke_lambda__using_lambda_(self):
        event = {'name' : 'world'}
        assert self.lambda_.invoke(event) == 'From lambda code, hello world'