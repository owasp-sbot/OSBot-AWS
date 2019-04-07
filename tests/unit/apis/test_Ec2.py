import sys ;

from osbot_aws.apis.Ec2 import Ec2

sys.path.append('..')

from unittest import TestCase

from pbx_gs_python_utils.utils.Dev import Dev


class test_Ec2(TestCase):
    def setUp(self):
        self.ec2 = Ec2()

    def test__init__(self):
        assert type(self.ec2.ec2).__name__ == 'EC2'

    def test_instances_details(self):
        result = self.ec2.instances_details()
        assert len(result) > 5

    def test_security_groups(self):
        result = self.ec2.security_groups()
        assert len(result) > 0

    def test_subnets(self):
        result = self.ec2.subnets()
        Dev.pprint(result)
        assert len(result) > 0

    def test_vpcs(self):
        result = self.ec2.vpcs()
        assert len(result) > 0
