from unittest import TestCase

from osbot_aws.apis.EC2 import EC2
from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC


class test_Temp_VPC(TestCase):

    def setUp(self) -> None:
        self.ec2 = EC2()

    def test__enter__exit__(self):
        temp_vpc = Temp_VPC(add_internet_gateway=True, add_route_table=True, add_security_group=True, add_subnet=True)

        with temp_vpc:
            vpc_id              = temp_vpc.vpc.vpc_id
            internet_gateway_id = temp_vpc.vpc.internet_gateway_id
            security_group_id   = temp_vpc.vpc.security_group_id
            subnet_id           = temp_vpc.vpc.subnet_id
            route_table_id      = temp_vpc.vpc.route_table_id

            assert self.ec2.internet_gateway_exists (internet_gateway_id) is True
            assert self.ec2.security_group_exists   (security_group_id  ) is True
            assert self.ec2.subnet_exists           (subnet_id          ) is True
            assert self.ec2.route_table_exists      (route_table_id     ) is True
            assert self.ec2.vpc_exists              (vpc_id             ) is True

            assert self.ec2.internet_gateway        (internet_gateway_id).get('Attachments') == [{'State': 'available', 'VpcId': vpc_id}]


        assert self.ec2.internet_gateway_exists (internet_gateway_id) is False
        assert self.ec2.security_group_exists   (security_group_id  ) is False
        assert self.ec2.subnet_exists           (subnet_id          ) is False
        assert self.ec2.route_table_exists      (route_table_id     ) is False
        assert self.ec2.vpc_exists              (vpc_id             ) is False