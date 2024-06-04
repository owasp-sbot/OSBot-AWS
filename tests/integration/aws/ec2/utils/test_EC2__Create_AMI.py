import pytest

from osbot_aws.aws.ec2.EC2_Instance import EC2_Instance
from osbot_aws.aws.ec2.utils.EC2__Create__AMI   import EC2__Create__AMI
from osbot_aws.aws.ec2.utils.TestCase__EC2      import TestCase__EC2
from osbot_utils.decorators.methods.capture_exception import capture_exception
from osbot_utils.utils.Dev                      import pprint


@pytest.mark.skip("only to be executed from the CI pipeline")
class test_EC2__Create__AMI(TestCase__EC2):

    def setUp(self):
        self.ec2_create_ami = EC2__Create__AMI(ec2=self.ec2)
        self.ec2_create_ami.ec2_create_instance.ec2 = self.ec2

    def test_create_instance(self):
        instance_id = self.ec2_create_ami.create_instance()
        pprint(instance_id)

    def test_create_ami__for__osbot_aws(self):
        self.ec2_create_ami.create_ami__for__osbot_aws()       # todo , add workflow to wait for the ami to be created and then stop the instance

    def test_create_ami__for__osbot_fastapi(self):
        self.ec2_create_ami.create_ami__for__osbot_fast_api()