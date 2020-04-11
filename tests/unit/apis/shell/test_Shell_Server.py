from unittest import TestCase

from osbot_aws.apis.shell.Shell_Server import Shell_Server
from osbot_utils.utils.Dev import Dev


class test_Shell_Server(TestCase):

    def setUp(self) -> None:
        self.server = Shell_Server()
        self.result = None

    def tearDown(self) -> None:
        if self.result is not None:
            Dev.pprint(self.result)

    def _shell_invoke(self, method_name, method_kwargs=None):
        event = {'shell': {'method_name': method_name, 'method_kwargs': method_kwargs}}
        return self.server.invoke(event)

    # test methods
    def test_invoke(self):
        assert self.server.invoke({}) is None
        assert self.server.invoke({'shell': {'method_name':'ping', 'method_kwargs': {}}}) == 'pong'
        assert self.server.invoke({'shell': {'method_name':'aaaa', 'method_kwargs': {}}}) is None
        assert self._shell_invoke('ping', {}  ) == 'pong'
        assert self._shell_invoke('ping', None) == 'pong'


    def test_invoke__process_run(self):
        assert 'tests/unit/apis/shell' in self._shell_invoke('process_run', {'executable':'pwd'}).get('stdout')


    def test_bash(self):
        assert 'test_Shell_Server.py' in self.server.bash('ls'    ).get('stdout')
        assert 'bin'                  in self.server.bash('ls /'  ).get('stdout')
        assert 'bin'                  in self.server.bash('ls','/').get('stdout')
        assert self.server.bash('AAAAAa').get('stderr') == 'bash: AAAAAa: command not found\n'


    def test_pwd(self):
        assert 'tests/unit/apis/shell' in self.server.pwd()

    def test_python_exec(self):
        assert self.server.python_exec('result=40+2') == 42
        assert len(self.server.python_exec('import sys;\npath = sys.path\nresult=path')) > 10