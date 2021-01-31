from unittest import TestCase

import pytest

from osbot_aws.apis.SSM import OSBot_AWS__SSM
from osbot_utils.utils.Dev import pprint


@pytest.mark.skip('need ec2 instance with ssm enabled')                 # add methods to configure and add SSM to server
class test_OSBot_AWS__SSM(TestCase):

    def setUp(self):
        self._ = OSBot_AWS__SSM()
        print()

    def test_command_run(self):
        instance_id = 'i-06298c4377973f455'                             # todo use instance created that supports ssm
        command     = 'ls /'
        result = self._.command_run(instance_id, command)

        pprint(result)

    def test_commands_list(self):
        instance_id = 'i-06298c4377973f455'
        command_id= '18f8de5e-116d-4245-89d0-f01f07310ef1'
        #result = self._.commands_list()
        #pprint(result)
        output = self._.client.get_command_invocation(
            CommandId=command_id,
            InstanceId=instance_id,
            )
        pprint(output)