from unittest import TestCase

from osbot_aws.apis.test_helpers.Temp_EC2_Instance import Temp_EC2_Instance
from osbot_utils.utils.Dev import pprint


class test_Temp_EC2_Instance(TestCase):

    def test__enter__exit(self):
        with Temp_EC2_Instance() as ec2_instance:
            assert ec2_instance.state() == {'Code': 0, 'Name': 'pending'}
        assert ec2_instance.state() == {'Code': 32, 'Name': 'shutting-down'}