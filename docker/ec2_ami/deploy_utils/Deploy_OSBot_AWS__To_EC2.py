from os import environ

from docker.ec2_ami import deploy_utils
from osbot_aws.AWS_Config import AWS_Config
from osbot_aws.apis.EC2 import EC2
from osbot_aws.aws.s3.S3__with_temp_role import S3__with_temp_role
from osbot_aws.aws.sts.STS import STS
from osbot_aws.helpers.EC_Instance import EC2_Instance
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Env import load_dotenv
from osbot_utils.utils.Files import path_combine, file_exists
from osbot_utils.utils.Status import status_error

AMIS_PER_REGION = {'eu-west-1': 'ami-0136026a91d5f4151', # AMI created with python installed
                   'eu-west-2': 'ami-008ea0202116dbc56' }


class Deploy_OSBot_AWS__To_EC2(Kwargs_To_Self):
    ec2          : EC2
    aws_config   : AWS_Config
    #ec2_instance: EC2_Instance

    def load_dotenv(self):
        env_file = path_combine(deploy_utils.path, '.env')
        assert file_exists(env_file)
        load_dotenv(env_file, override=True)

    def create_kwargs(self, image_id=None):
        load_dotenv()
        instance_type        = 't3.nano'
        spot_instance        = True
        iam_role_name        = self.role_to_assign_EC2_instance()
        security_group_id    = environ.get('EC2_TESTS__SECURITY_GROUP_ID')
        ssh_key_name         = environ.get('EC2_TESTS__PATH_SSH_KEY_FILE_NAME')
        iam_instance_profile = {'Name': iam_role_name }              #"environ.get('EC2_TESTS__IAM_ROLE_TO_ASSUME')

        return  dict(image_id             = image_id or 'ami-008ea0202116dbc56' ,
                     iam_instance_profile = iam_instance_profile                   ,
                     key_name             = ssh_key_name                        ,
                     security_group_id    = security_group_id                   ,
                     instance_type        = instance_type                       ,
                     spot_instance        = spot_instance                       )

    def ec2_instance(self, instance_id):
        return EC2_Instance(instance_id=instance_id)

    def instance_info(self, instance_id):
        return self.ec2.instance_details(instance_id)

    def role_to_assign_EC2_instance(self):
        iam_assume_role = S3__with_temp_role().iam_assume_role()
        iam_assume_role.create_role(create_credentials=False)
        return iam_assume_role.role_name

    def running_instances(self):
        return self.ec2.instances_details()

    def start_instance(self,image_id=None):
        try:
            ec2_instance = EC2_Instance()
            ec2_instance.create_kwargs = self.create_kwargs(image_id=image_id)
            pprint(ec2_instance.create_kwargs)
            #region_name  = self.aws_config.region_name()
            #image_id     = AMIS_PER_REGION.get(region_name)
            return ec2_instance.create()
        except Exception as e:
            return status_error(message='failed to create EC2 instance',
                                error=str(e))

    def stop_instance(self, instance_id):
        return self.ec2.instance_terminate(instance_id)



    def ssh(self, instance_id):
        ec2_instance = EC2_Instance(instance_id=instance_id)
        ssh_key_file = environ.get('EC2_TESTS__PATH_SSH_KEY_FILE')
        ssh_key_user = environ.get('EC2_TESTS__PATH_SSH_KEY_USER')
        return ec2_instance.ssh(ssh_key_file=ssh_key_file, ssh_key_user=ssh_key_user)




