from unittest import TestCase
from gw_bot.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.shell.Shell_Client import Shell_Client
from osbot_utils.utils.Dev import Dev


class test_Shell_Client(TestCase):

    def setUp(self) -> None:
        self.client = Shell_Client()
        self.result = None

    def tearDown(self) -> None:
        if self.result is not None:
            Dev.pprint(self.result)

    def test_bash(self):
        assert 'test_Shell_Server.py' in self.client.bash('ls'    ).get('stdout')
        assert 'bin'                  in self.client.bash('ls /'  ).get('stdout')
        assert 'bin'                  in self.client.bash('ls','/').get('stdout')
        assert self.client.bash('AAAAAa').get('stderr') == 'bash: AAAAAa: command not found\n'

    def test_ls(self):
        assert 'test_Shell_Client.py' in self.client.ls()
        assert ''                     == self.client.ls('aaaa')
        assert 'bin'                  in self.client.ls('/')
        assert 'bin'                  in self.client.ls('' , '/')
        assert 'bash'                 in self.client.ls('bin', '/')

    def test_process_run(self):
        assert 'tests/unit/apis/shell' in self.client.process_run('pwd').get('stdout')

    def test_pwd(self):
        assert 'tests/unit/apis/shell' in self.client.pwd()

class test_Shell_Client_Lambda(Test_Helper):

    def setUp(self) -> None:
        super().setUp()
        #self.lambda_name = 'osbot_aws.lambdas.shell.lambda_shell'
        self.lambda_name = 'osbot_browser.lambdas.lambda_browser'
        self.client = Shell_Client(self.lambda_name)

    #@trace(include=['test*','unit*'], exclude=['osbot_utils*'])
    def test_lambda_pwd_exec(self):
        assert self.client.pwd()          == '/var/task\n'
        assert self.client.exec('uname')  == 'Linux'
        assert self.client.exec('whoami') == 'sbx_user1051'
        assert self.client.exec('whoami') == self.client.whoami()

    def test_lambda_ping(self):
        assert self.client.ping() == 'pong'

    def test_list_processes(self):
        print(self.client.list_processes())

    def test_memory_usage(self):
        print(self.client.memory_usage())