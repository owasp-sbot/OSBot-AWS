from unittest import TestCase

import pytest

from osbot_aws.helpers.Lambda_SSH import Lambda_SSH


# see also the tests in test_Lambda_SSH (which already cover this function
@pytest.mark.skip()                 # todo: refactor to take into account the need to create a temp SSH server
class test_server_ssh(TestCase):

    def setUp(self) -> None:
        self.key_name   = 'packer.pem'
        self.server_ssh = Lambda_SSH(key_name=self.key_name)

    #def test_deploy(self):
    #    self.server_ssh.deploy_lambda()

    def test_invoke(self):
        assert type(self.server_ssh.invoke_lambda('ls')) is str
