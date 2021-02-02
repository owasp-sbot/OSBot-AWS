from unittest import TestCase

from osbot_aws.apis.EC2 import EC2
from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC


class test_Temp_VPC(TestCase):

    def setUp(self) -> None:
        self.ec2 = EC2()

    def test__enter__exit__(self):
        with Temp_VPC() as temp_vpc:
            vpc_id              = temp_vpc.vpc_id
            internet_gateway_id = temp_vpc.internet_gateway_id
            assert self.ec2.vpc_exists             (vpc_id             ) is True
            assert self.ec2.internet_gateway_exists(internet_gateway_id) is True
            assert self.ec2.internet_gateway       (internet_gateway_id).get('Attachments') == [{'State': 'available', 'VpcId': vpc_id}]

        assert self.ec2.vpc_exists             (vpc_id             ) is False
        assert self.ec2.internet_gateway_exists(internet_gateway_id) is False
