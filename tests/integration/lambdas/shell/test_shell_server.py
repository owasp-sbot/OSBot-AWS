from osbot_aws.deploy.Deploy_Lambda import Deploy_Lambda
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.lambdas.shell.shell_server import run
from osbot_utils.utils.Dev import pprint

class test_run_command(Test_Helper):
    def setUp(self):
        super().setUp()
        self.handler     = run
        self.aws_lambda  = Deploy_Lambda(self.handler)

    def test_invoke_directly(self):
        #self.result = run({'method_name': 'pwd'},{})
        self.result = run({'method_name': 'python_exec','method_kwargs': {'code': 'result=40+2' }})

    def test_update_lambda_function(self):
        self.aws_lambda.add_osbot_aws().deploy()
        self.result = self.aws_lambda.invoke({'method_name': 'ping'})

    # test the invocation
    def test_invoke(self):
        #self.test_update_lambda_function()
        pprint(self.aws_lambda.invoke({'method_name': 'ping'          }).get('return_value'))
        pprint(self.aws_lambda.invoke({'method_name': 'pwd'           }).get('return_value'))
        pprint(self.aws_lambda.invoke({'method_name': 'disk_space'    }).get('return_value'))
        pprint(self.aws_lambda.invoke({'method_name'  : 'python_exec',
                                       'method_kwargs': {'code':"result=40+2"}}))

