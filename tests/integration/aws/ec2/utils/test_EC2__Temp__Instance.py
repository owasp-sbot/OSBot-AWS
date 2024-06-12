import pytest

from osbot_aws.aws.ec2.utils.EC2__Temp__Instance import EC2__Temp__Instance
from osbot_aws.aws.ec2.utils.TestCase__EC2 import TestCase__EC2
from osbot_utils.decorators.methods.capture_exception import capture_exception
from osbot_utils.utils.Dev import pprint


@pytest.mark.skip("will create an EC2 instance so skip for now")
class test_EC2__Temp__Instance(TestCase__EC2):

    def test___enter__exit__(self):
        ec2_temp_instance = EC2__Temp__Instance(wait_for_ssh=False, ec2=self.ec2)
        with ec2_temp_instance as _:
            assert _.ec2_instance_id       is not None
            assert _.ec2_instance.exists() is True

        assert ec2_temp_instance.ec2_instance.state().get('Name') == 'shutting-down'

    @pytest.mark.skip("No need to run this all the time")
    def test_wait_for_ssh(self):
        ec2_temp_instance = EC2__Temp__Instance(ec2=self.ec2)
        assert ec2_temp_instance.wait_for_ssh is True

        with ec2_temp_instance as _:
            assert _.ec2_instance_id is not None
            assert _.ec2_instance.exists() is True
            assert _.ssh().ssh_linux().pwd() == '/home/ec2-user'

        assert ec2_temp_instance.ec2_instance.state().get('Name') == 'shutting-down'