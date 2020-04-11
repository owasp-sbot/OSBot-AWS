from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell


class test_Lambda_Shell(Test_Helper):

    def setUp(self):
        super().setUp()
        self.lambda_shell = Lambda_Shell()

    def test_get_lambda_shell_auth__reset_lambda_shell_auth(self):
        self.lambda_shell.reset_lambda_shell_auth()
        self.result = self.lambda_shell.get_lambda_shell_auth()