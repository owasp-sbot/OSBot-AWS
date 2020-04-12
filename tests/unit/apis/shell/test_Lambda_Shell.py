from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.shell.Lambda_Shell import Lambda_Shell, lambda_shell


class test_Lambda_Shell(Test_Helper):

    def setUp(self):
        super().setUp()
        self.lambda_shell = Lambda_Shell({})

    def test_reset_lambda_shell_auth(self):
        self.lambda_shell.reset_lambda_shell_auth()
        assert len(self.lambda_shell.get_lambda_shell_auth().get('key').split('-')) == 5

    def test_get_lambda_shell_auth(self):
        #todo: add support to confirming that this method will be fast with the @cache_in_tmp decorator
        for i in range(1,5):
            self.lambda_shell.get_lambda_shell_auth()

    def test_valid_shell_request(self):
        assert self.lambda_shell.valid_shell_request() is False
        self.lambda_shell.shell_command = {'method_name':'ping', 'auth_key': self.lambda_shell.get_lambda_shell_auth()}
        assert self.lambda_shell.valid_shell_request() == True

    def test_has_shell_invoke(self):
        self.lambda_shell.shell_command = {'method_name': 'ping', 'auth_key': self.lambda_shell.get_lambda_shell_auth()}
        assert self.lambda_shell.invoke() == 'pong'

        self.lambda_shell.shell_command['method_name'] = 'aaaa'         # method doesn't exist
        self.lambda_shell.invoke() == None

    def test_decorator_lambda_shell(self):
        @lambda_shell
        def lambda_run(event, context=None):
            return 'here'

        payload = {'shell':  {'method_name': 'ping', 'auth_key': self.lambda_shell.get_lambda_shell_auth()} }
        assert lambda_run(payload) == 'pong'

