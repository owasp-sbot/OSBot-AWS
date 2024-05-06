import json
from osbot_aws.aws.apigateway.lambdas.Deploy__lambda_web_sockets import Deploy__lambda_web_sockets
from osbot_aws.testing.TestCase__Lambda                          import TestCase__Lambda
from osbot_utils.utils.Dev                                       import pprint

class test_Deploy__lambda_web_sockets(TestCase__Lambda):

    def setUp(self):
        self.deploy = Deploy__lambda_web_sockets()

        aws_lambda             = self.deploy.deploy_lambda.lambda_function()
        aws_lambda.client      = self.client__lambda
        aws_lambda.s3          = self.type_S3

    # def test_update_config(self):
    #     result = self.deploy.update_config()
    #     pprint(result)

    def test__update(self):
        result = self.deploy.update()
        assert result == 'Successful'

    def test_invoke__locally(self):
        payload = {}
        context = {}
        assert self.deploy.handler(payload, context) == {'body': 'Route not recognized.', 'statusCode': 400}

    def test_invoke__lambda(self):
        lambda_ = self.deploy.deploy_lambda.lambda_function()

        assert lambda_.invoke() == {'statusCode': 400, 'body': 'Route not recognized.'}
