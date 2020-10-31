from gw_bot.Deploy import Deploy
from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda import Lambda
from osbot_aws.apis.Lambda_Layer import Lambda_Layer


class test_run_command(Test_Helper):
    def setUp(self):
        super().setUp()
        self.lambda_name = 'osbot_aws.lambdas.dev.lambda_layer'
        self.aws_lambda   = Lambda(self.lambda_name)

    ## helpers
    def layer_version_arn(self):
        package_name = 'requests'
        layer_name = package_name
        layer = Lambda_Layer(layer_name)
        if layer.exists() is False:
            self.result = layer.create_from_pip(package_name)
        return layer.latest().get('LayerVersionArn')

    ## tests
    def test_update(self):
        Deploy().deploy_lambda__gw_bot(self.lambda_name)

    def test_update_and_invoke(self):
        self.test_update()
        self.result = self.aws_lambda.invoke()

    def test_set_layers(self):
        layer_version_arn = self.layer_version_arn()
        self.aws_lambda.set_layers([layer_version_arn])
        self.result = self.aws_lambda.update_lambda_configuration()
        #self.result = self.aws_lambda.info()

    def test_install_layer(self):
        self.aws_lambda.delete()
        self.test_update()
        self.test_set_layers()
        shell = self.aws_lambda.shell()
        self.result = shell.ls('/opt')

    def test_execute_command(self):
        code = """
import sys
#sys.path.append('/opt')        
import requests        
result = requests.get('https://www.google.com/404').text      
"""
        shell = self.aws_lambda.shell()
        self.result = shell.python_exec(code)





