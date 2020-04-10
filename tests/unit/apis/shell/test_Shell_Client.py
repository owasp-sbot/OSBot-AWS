from unittest import TestCase

from osbot_aws.apis.shell.Shell_Client import Shell_Client
from osbot_aws.apis.shell.Shell_Server import Shell_Server
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

class test_Shell_Client_Lambda(TestCase):

    def setUp(self) -> None:
        self.lambda_name = 'osbot_aws.lambdas.shell.lambda_shell'
        self.client = Shell_Client(self.lambda_name)

    def test_lambda_pong(self):
        assert self.client.pwd()          == '/var/task\n'
        assert self.client.exec('uname')  == 'Linux'
        assert self.client.exec('whoami') == 'sbx_user1051'