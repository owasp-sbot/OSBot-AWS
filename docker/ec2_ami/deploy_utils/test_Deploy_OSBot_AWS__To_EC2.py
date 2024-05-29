from unittest import TestCase

from docker.ec2_ami.deploy_utils.Deploy_OSBot_AWS__To_EC2 import Deploy_OSBot_AWS__To_EC2
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Functions import function_source_code
from osbot_utils.utils.Misc import base64_to_str


class test_Deploy_OSBot_AWS__To_EC2(TestCase):
    deploy_to_ec2 : Deploy_OSBot_AWS__To_EC2

    @classmethod
    def setUpClass(cls) -> None:
        cls.deploy_to_ec2 = Deploy_OSBot_AWS__To_EC2()
        cls.deploy_to_ec2.load_dotenv()

    def test_start_instance(self):
        with self.deploy_to_ec2 as _:
            instance_id = _.start_instance()
            pprint(instance_id)

    def test_stop_instance(self):
        with self.deploy_to_ec2 as _:
            instance_id = 'i-075ce03f491abfe77'
            result = _.stop_instance(instance_id)
            pprint(result)

    def test_instance_info(self):
        instance_ids = ['i-0160d310c454aca75']
        instance_id  = instance_ids[0]

        with self.deploy_to_ec2 as _:
            info = _.instance_info(instance_id)
            pprint(info)

    def test_instance_ssh(self):
        instance_id = 'i-0160d310c454aca75'
        print()
        print(f'>>> commands executed in instance: {instance_id}')
        with self.deploy_to_ec2.ssh(instance_id) as _:
            #assert _.execute_command__return_stdout('python3 --version') == 'Python 3.9.16'
            #assert 'Linux ' in _.execute_command__return_stdout('uname -a'))
            #pprint(_.execute_command('sudo yum update -y'))
            #pprint(_.execute_command('sudo yum install python3-pip -y'))
            #assert _.execute_command__return_stdout('pip3 --version') == 'pip 21.3.1 from /usr/lib/python3.9/site-packages/pip (python 3.9)'
            #pprint(_.execute_command__return_stdout('pip3 uninstall -y osbot-aws'))
            pprint(_.execute_command__return_stderr('pip3 install osbot-aws==2.9.0'))
            #pprint(_.execute_command__return_stdout('pip3 install osbot-utils'))
            #assert _.execute_command__return_stdout('python3 -c "print(\'Hello, World!\')"') == 'Hello, World!'
            multi_line_command = """
import sys
print(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
"""
            #assert '3.9.16' in _.execute_command__return_stdout(multi_line_command)
            #assert _.execute_python__code__return_stdout(multi_line_command) == '3 9 16'#

            # def an_function():
            #     return 'Hello from the EC2 instance!'
            # assert _.execute_python__function(an_function).get('stdout') == 'Hello from the EC2 instance!\n'
            #pprint(exec_code)

            # def test_osbot_utils():
            #     from osbot_utils.utils.Misc import str_to_base64
            #     an_value = 'this will be base64 encoded!'
            #     return str_to_base64(an_value)
            #
            # function_return_value = _.execute_python__function__return_stdout(test_osbot_utils)
            # assert base64_to_str(function_return_value) == 'this will be base64 encoded!'

            def test_osbot_aws():
                from osbot_aws.aws.sts.STS import STS
                sts = STS()
                return f'here : {sts}'

            pprint( _.execute_python__function__return_stderr(test_osbot_aws))
            # function_return_value = _.execute_python__function__return_stdout(test_osbot_aws)
            # assert base64_to_str(function_return_value) == 'this will be base64 encoded!'

            #   assert _.execute_python__function(test_osbot_utils).get('stdout') == 'Hello from the EC2 instance!\n'






