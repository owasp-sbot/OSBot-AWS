from osbot_aws.aws.ec2.utils.EC2__Temp__Instance import EC2__Temp__Instance
from osbot_aws.aws.ec2.utils.TestCase__EC2 import TestCase__EC2
from osbot_utils.decorators.methods.capture_exception import capture_exception
from osbot_utils.utils.Dev import pprint


class test_EC2__Temp__Instance(TestCase__EC2):

    @capture_exception
    def test___enter__exit__(self):
        wait_for_ssh = False
        ec2_temp_instance = EC2__Temp__Instance(wait_for_ssh=wait_for_ssh, ec2=self.ec2)
        with ec2_temp_instance as _:
            assert _.ec2_instance_id       is not None
            assert _.ec2_instance.exists() is True

        assert ec2_temp_instance.ec2_instance.state().get('Name') == 'shutting-down'