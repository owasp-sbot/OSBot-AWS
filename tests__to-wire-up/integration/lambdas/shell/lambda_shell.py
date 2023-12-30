from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell
from osbot_aws.deploy.Deploy_Lambda       import Deploy_Lambda
from osbot_aws.helpers.Test_Helper        import Test_Helper
from osbot_aws.lambdas.shell.lambda_shell import  run
from osbot_utils.utils.Dev import pprint

class test_run_command(Test_Helper):
    def setUp(self):
        super().setUp()
        self.handler      = run
        self.aws_lambda   = Deploy_Lambda(self.handler)
        self.lambda_shell = Lambda_Shell()

    def test_invoke_directly(self):
        assert run({}) == 'in lambda shell'
        auth_key = self.lambda_shell.get_lambda_shell_auth()
        pprint(auth_key)
        self.result = run({'lambda_shell': {'method_name' : 'ping',
                                            'auth_key'    : auth_key }})

    def test_update_lambda_function(self):
        self.aws_lambda.add_osbot_aws().deploy()
        assert self.aws_lambda.invoke({}) == 'in lambda shell'

    def test_invoke_shell_cmd(self):
        self.aws_lambda.add_osbot_aws().deploy()
        auth_key      = self.lambda_shell.get_lambda_shell_auth()
        method_name   = 'ping'
        method_kwargs = {}
        payload       = {'lambda_shell': {'method_name'  : method_name  ,
                                          'method_kwargs': method_kwargs,
                                          'auth_key'     : auth_key     }}
        self.result = self.aws_lambda.invoke(payload)
