from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.Lambda_Docker import Lambda_Docker


class test_Lambda_Http(Test_Helper):

    def setUp(self):
        super().setUp()
        self.lambda_docker = Lambda_Docker()

    def test_run_bash(self):
        assert self.lambda_docker.run_bash('pwd').get('stdout') == '/var/task\n'