import pytest
from unittest import TestCase

from osbot_aws.apis.SSM import SSM
from osbot_utils.utils.Dev import pprint




class test_OSBot_AWS__SSM(TestCase):

    def setUp(self):
        self.ssm = SSM()
        print()


    @pytest.mark.skip('need ec2 instance with ssm enabled')                 # todo add methods to configure and add SSM to server
    def test_command_run(self):
        instance_id = 'i-06298c4377973f455'                                 # todo use instance created that supports ssm
        command     = 'ls /'
        result = self._.command_run(instance_id, command)

        pprint(result)

    @pytest.mark.skip('need ec2 instance with ssm enabled')
    def test_commands_list(self):
        instance_id = 'i-06298c4377973f455'                                 # todo: refactor into ssm method
        command_id= '18f8de5e-116d-4245-89d0-f01f07310ef1'
        #result = self._.commands_list()
        #pprint(result)
        output = self._.client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
            )
        pprint(output)

    def test_parameters(self):
        filter_value = '/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2'
        result = self.ssm.parameters(filter_value, index_by='Name')
        assert len(result) == 1
        assert result[filter_value].get('Name') == filter_value
