
from osbot_aws.aws.ec2.EC2 import EC2
from osbot_aws.aws.ec2.EC2_Instance import EC2_Instance
from osbot_aws.aws.ec2.utils.EC2__Create__Instance import EC2__Create__Instance
from osbot_aws.utils.Version import Version
from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Misc import random_id, random_uuid_short

# todo , add methods to wait for the ami to be created and then stop the instance
class EC2__Create__AMI(Type_Safe):
    ec2_create_instance : EC2__Create__Instance
    ec2_instance        : EC2_Instance          = None
    instance_id         : str
    ami_name            : str
    ec2                 : EC2

    def create_instance(self):
        self.instance_id  = self.ec2_create_instance.create_instance__with_amazon_linux__t3_nano__ssh_sg__spot()
        self.ec2_instance = EC2_Instance(instance_id=self.instance_id, ec2=self.ec2)
        return self

    def create_ami_from_instance_id(self):
        instance_id = self.instance_id
        if not self.ami_name:
            self.ami_name = f'osbot-ami-{self.instance_id}-{random_uuid_short()}'
        return self.ec2_create_instance.ec2.create_image(instance_id=instance_id, name=self.ami_name)

    def ssh(self):
        return self.ec2_instance.ssh(self.ec2_create_instance.path_key_file(),'ec2-user' )

    def install_python_and_osbot_aws(self):
        self.ec2_instance.wait_for_ssh()
        with self.ssh() as _:
            _.ssh_execute().print_after_exec = True
            _.ssh_linux_amazon().install_python3()
            _.ssh_linux_amazon().pip_install('osbot_aws')

    def install_fastapi(self):
        with self.ssh() as _:
            _.ssh_linux_amazon().pip_install('fastapi')



    def create_ami__for__osbot_aws(self):
        region_name         = self.ec2_create_instance.ec2.aws_config.region_name()
        osbot_version       = Version().value()
        self.ami_name      = f'osbot-aws__{region_name}__{osbot_version}'
        self.create_instance()
        self.install_python_and_osbot_aws()
        self.create_ami_from_instance_id()

    def create_ami__for__osbot_fast_api(self):
        region_name = self.ec2_create_instance.ec2.aws_config.region_name()
        osbot_version = Version().value()
        self.ami_name = f'osbot-fastapi___{osbot_version}___{region_name}'
        self.create_instance()
        self.install_python_and_osbot_aws()
        self.install_fastapi()
        self.create_ami_from_instance_id()

