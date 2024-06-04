from unittest import TestCase

from osbot_aws.helpers.EC2_Instance import EC2_Instance


class test_EC2_Instance(TestCase):

    def setUp(self):
        self.ec2_instance = EC2_Instance()

    def test_create(self):
        self.ec2_instance.create()
        assert self.ec2_instance.state() ==  {'Code': 0, 'Name': 'pending'}
        self.ec2_instance.delete()
        assert self.ec2_instance.state() == {'Code': 32, 'Name': 'shutting-down'}
