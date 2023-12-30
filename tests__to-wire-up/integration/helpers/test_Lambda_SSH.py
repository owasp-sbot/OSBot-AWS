from unittest import TestCase

import pytest
from osbot_utils.utils.Dev          import pprint
from osbot_utils.utils.Files        import path_combine, file_exists
from osbot_aws.helpers.Lambda_SSH   import Lambda_SSH
from osbot_aws.apis.Secrets         import Secrets

@pytest.mark.skip("needs setup that creates a temp server to ssh into")
class test_Lambda_SSH(TestCase):

    @classmethod
    def setUpClass(cls) -> None:

        #cls.es_index_ec2_data = ES_Index("ec2-data-raw").setup()
        #cls.ec2_instances      = cls.es_index_ec2_data.instances_to_ssh_with_key(cls.key_name)
        #assert len(cls.ec2_instances) > 0
        #cls.ec2_instance       = cls.ec2_instances.pop()
        #cls.target_host        = cls.ec2_instance.get('public_ip_address')
        #assert cls.target_host is not None

        cls.key_name = 'packer'                         # todo: add support for creating a temp EC2 server to test this
        cls.target_host = "54.74.165.194"               #       at the moment these tests need an hardcoded IP of a valid server and key_name

    def setUp(self) -> None:
        self.lambda_ssh = Lambda_SSH(key_name=self.key_name, target_host=self.target_host)

    def test_deploy_lambda(self):
        assert self.lambda_ssh.deploy_lambda()

    def test_access_to_aws_secrets(self):
        secret_name = f'ssh_key_{self.key_name}.pem'
        assert len(Secrets('').list()) > 0
        assert Secrets(secret_name).exists() is True

    def test_get_key_from_secret_store(self):
        assert '-----BEGIN RSA PRIVATE KEY-----' in self.lambda_ssh.get_key_from_secret_store()

    @pytest.mark.skip()                                 # todo: refactor to use a temp key (and confirm all is working ok)
    def test_upload_ssh_key_to_secret_store(self):
        load_path_to_keys = '...'
        path_to_ssh_key   = path_combine(load_path_to_keys, self.key_name + ".pem")
        assert file_exists(path_to_ssh_key)
        pprint(self.lambda_ssh.upload_ssh_key_to_secret_store(path_to_ssh_key))

    # def test_deploy_and_invoke_lambda(self):
    #     assert self.lambda_ssh.deploy_lambda()
    #     ssh_command = 'uname'
    #     result = self.lambda_ssh.invoke_lambda(ssh_command)
    #     pprint(result)

    def test_invoke_lambda(self):
        ssh_command = 'uname'
        result = self.lambda_ssh.invoke_lambda(ssh_command)
        assert result == 'Linux\n'

    # def test_invoke_with_port_forward(self):          # not sure we need this
    #     port_forward = {"local_port": 8080 ,
    #                     "remote_ip" : }