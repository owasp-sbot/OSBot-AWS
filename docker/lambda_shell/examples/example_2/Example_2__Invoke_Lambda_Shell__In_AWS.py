from os import getenv
from unittest import TestCase

from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell, SHELL__ENV_VAR__AUTH_KEY
from osbot_aws.apis.shell.Shell_Client import Shell_Client
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Env import load_dotenv
from osbot_utils.utils.Files import path_combine


class Example_2__Invoke_Lambda_Shell__In_AWS:

    def __init__(self):
        self.lambda_name     = 'asd'
        self.lambda_function = Lambda('lambda_shell')
        self.lambda_shell    = Shell_Client(self.lambda_function)

    def invoke_lambda_function(self,payload):
        return self.lambda_function.invoke()
        #return self.lambda_shell.invoke(self.lambda_name, payload)



    def setup(self):
        env_file = path_combine(__file__, '../.env')
        load_dotenv(env_file)
        return self

class test_Example_2__Invoke_Lambda_Shell__In_AWS(TestCase):

    def setUp(self):
        self.example = Example_2__Invoke_Lambda_Shell__In_AWS().setup()

    def test_setup(self):
        assert getenv(SHELL__ENV_VAR__AUTH_KEY) is not None

    def test_invoke_lambda_function(self):
        assert self.example.invoke_lambda_function({})  == {'body': 'this is not from lambda shell', 'statusCode': 200}

    def test_invoke_lambda_shell(self):
        #assert self.example.lambda_shell.ping() == 'pong'
        #assert self.example.lambda_shell.pwd () == '/var/task\n'

        def get_var():
            from os import getenv
            return f"the value is : {getenv('SHELL_VAR')}"

        assert self.example.lambda_shell.exec_function(get_var) == 'the value is : 42'


