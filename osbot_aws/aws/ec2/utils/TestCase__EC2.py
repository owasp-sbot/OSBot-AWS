from unittest import TestCase

from osbot_aws.aws.ec2.EC2 import EC2
from osbot_aws.aws.ec2.utils.EC2__with_temp_role import EC2__with_temp_role


class TestCase__EC2(TestCase):
    ec2        : EC2

    @classmethod
    def setUpClass(cls):
        cls.ec2      = EC2__with_temp_role()

    @classmethod
    def tearDownClass(cls):
        pass