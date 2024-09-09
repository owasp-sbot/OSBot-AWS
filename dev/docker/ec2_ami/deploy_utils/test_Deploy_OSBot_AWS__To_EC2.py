from unittest import TestCase

from docker.ec2_ami.deploy_utils.Deploy_OSBot_AWS__To_EC2 import Deploy_OSBot_AWS__To_EC2
from osbot_aws.aws.iam.IAM import IAM
from osbot_aws.aws.s3.S3__with_temp_role import S3__with_temp_role

from osbot_utils.testing.Logging import Logging
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Functions import function_source_code
from osbot_utils.utils.Misc import base64_to_str


class test_Deploy_OSBot_AWS__To_EC2(TestCase):
    deploy_to_ec2 : Deploy_OSBot_AWS__To_EC2

    @classmethod
    def setUpClass(cls) -> None:
        cls.deploy_to_ec2 = Deploy_OSBot_AWS__To_EC2()
        cls.deploy_to_ec2.load_dotenv()

    def test_setup_ec2_instance_role(self):
        with self.deploy_to_ec2 as _:
            role_for_ec2_instance = _.setup_ec2_instance_role()
            pprint(role_for_ec2_instance)
            #assert role_for_ec2_instance.exists() is True


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
        #with self.deploy_to_ec2.ssh(instance_id) as _:
            #assert _.execute_command__return_stdout('python3 --version') == 'Python 3.9.16'
            #assert 'Linux ' in _.execute_command__return_stdout('uname -a'))
            #pprint(_.execute_command('sudo yum update -y'))
            #pprint(_.execute_command('sudo yum install python3-pip -y'))
            #assert _.execute_command__return_stdout('pip3 --version') == 'pip 21.3.1 from /usr/lib/python3.9/site-packages/pip (python 3.9)'
            #pprint(_.execute_command__return_stdout('pip3 uninstall -y osbot-aws'))
            #pprint(_.execute_command__return_stdout('pip3 install osbot-aws'))
            #pprint(_.execute_command__return_stdout('pip3 install osbot-utils'))
            #assert _.execute_command__return_stdout('python3 -c "print(\'Hello, World!\')"') == 'Hello, World!'
#             multi_line_command = """
# import sys
# print(sys.version_info.major, sys.version_info.minor, sys.version_info.micro)
# """

            # def test_osbot_aws():
            #     from osbot_aws.aws.sts.STS import STS
            #     sts = STS()
            #     return f'iam details : {sts.caller_identity()}'
            #
            # assert 'assumed-role/ecsInstanceRole'  in  _.execute_python__function__return_stdout(test_osbot_aws)


    def test_create_ami(self):
        instance_id = 'i-0160d310c454aca75'
        name        = 'ami-with-osbot-aws'          # this created the ami 'ami-0062dc7f40a35e99a'
        with self.deploy_to_ec2 as _:
            new_image_id = _.ec2.create_image(instance_id, name)
            pprint(new_image_id)                # 'ami-0062dc7f40a35e99a'

    def test_new_image_details(self):
        new_image_id = 'ami-0062dc7f40a35e99a'
        with self.deploy_to_ec2 as _:
            image = _.ec2.image(new_image_id)
            pprint(image)

    def test_role_to_assign_EC2_instance(self):
        with self.deploy_to_ec2 as _:
            role_name = _.role_to_assign_EC2_instance()
            iam = IAM(role_name=role_name)
            assert iam.role_exists() is True

    def test_create_and_execute__image__with_osbot_utils(self):
        logging = Logging().enable_log_to_console()
        image_id = 'ami-0062dc7f40a35e99a'
        with self.deploy_to_ec2 as _:
            logging.info(f'Step 1: starting instance with image: {image_id}')
            instance_id  = _.start_instance(image_id)
            pprint(instance_id)

            ec2_instance = _.ec2_instance(instance_id)
            logging.info(f'Step 2: wait for ssh in instance: {instance_id}')
            ec2_instance.wait_for_ssh()
            ssh = _.ssh(instance_id)
            logging.info(f'Step 3: execute simple python command in instance')

            assert ssh.execute_command__return_stdout('python3 --version') == 'Python 3.9.16'

            logging.info(f'Step 3: execute iam check python command in instance')

            def test_osbot_aws():
                from osbot_aws.aws.sts.STS import STS
                from osbot_aws.aws.s3.S3   import S3
                sts = STS()
                s3  = S3()
                return f'iam details : {sts.caller_identity()}\ns3 buckets : {s3.buckets()}'
            result = ssh.execute_python__function__return_stdout(test_osbot_aws)
            logging.info(f'Step 4: confirm iam result is correct: {result}')
            pprint(result)
            ec2_instance.delete()

    def test_just_execute(self):
        instance_id = 'i-086fc0d421f06f57e'
        def test_osbot_aws():
            from osbot_aws.AWS_Config import AWS_Config
            aws_config = AWS_Config()
            aws_config.set_aws_session_region_name('eu-west-1')

            from osbot_aws.aws.s3.S3 import S3
            s3 = S3()
            return f's3 buckets : {s3.buckets()}'
            #return f'iam details : {ec2_instance.info()}'

        with self.deploy_to_ec2 as _:
            ssh = _.ssh(instance_id)
            result = ssh.execute_python__function__return_stdout(test_osbot_aws)
            #result = ssh.execute_python__function__return_stderr(test_osbot_aws)
            pprint(result)






