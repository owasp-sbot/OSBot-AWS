from osbot_aws.aws.ec2.EC2 import EC2
from osbot_aws.aws.ec2.EC2_Instance import EC2_Instance
from osbot_aws.aws.ec2.utils.EC2__Create__Instance import EC2__Create__Instance
from osbot_utils.base_classes.Type_Safe import Type_Safe


class EC2__Temp__Instance(Type_Safe):
    ec2_create_instance : EC2__Create__Instance  = None
    ec2_instance        : EC2_Instance           = None
    ec2_instance_id     : str
    wait_for_ssh        : bool                   = True
    ec2                 : EC2

    def __enter__(self):
        self.ec2_create_instance = EC2__Create__Instance(ec2=self.ec2)
        self.ec2_instance_id     = self.ec2_create_instance.create_instance__with_amazon_linux__t3_nano__ssh_sg__spot()
        self.ec2_instance        = EC2_Instance(instance_id=self.ec2_instance_id, ec2=self.ec2)
        if self.wait_for_ssh:
            self.ec2_instance.wait_for_ssh()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.ec2_instance.delete()
        return False

    def ssh(self):
        return self.ec2_instance.ssh(self.ec2_create_instance.path_key_file(), 'ec2-user')

