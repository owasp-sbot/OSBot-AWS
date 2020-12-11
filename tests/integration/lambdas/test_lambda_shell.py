#from gw_bot.Deploy import Deploy            # todo: refactor this code from gw_bot
import unittest
from unittest.case import skip

import pytest

from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.lambdas.shell.lambda_shell import run

@pytest.mark.skip('Fix tests')
class test_run_command(Test_Helper):
    def setUp(self):
        super().setUp()
        self.lambda_name = 'osbot_aws.lambdas.shell.lambda_shell'
        self.aws_lambda   = Lambda(self.lambda_name)

    def test_invoke_directly(self):
        self.result = run({'shell':{'method_name': 'pwd'}},{})

    def test_update_lambda_function(self):
        Deploy().deploy_lambda__gw_bot(self.lambda_name)

    # def test_add_layers(self):
    #     #layer = 'arn:aws:lambda:eu-west-1:311800962295:layer:test_simple_layer:1'
    #     layer = 'arn:aws:lambda:eu-west-1:764866452798:layer:chrome-aws-lambda:8'       # chrome
    #     layer = 'arn:aws:lambda:eu-west-1:764866452798:layer:libreoffice-brotli:1'      # libreoffice
    #     self.aws_lambda.configuration_update(Layers=[f'{layer}'])
    #     self.result = self.aws_lambda.info()

    # test the invocation
    def test_update_and_invoke(self):
        self.test_update_lambda_function()
        payload = {'shell':{'method_name': 'ping'}}
        self.result = self.aws_lambda.invoke(payload)

