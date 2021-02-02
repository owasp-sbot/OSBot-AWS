import sys ;

import pytest

from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC
from osbot_utils.utils.Misc               import list_index_by
from osbot_aws.apis.EC2                   import EC2
from unittest                             import TestCase
from osbot_utils.utils.Dev                import pprint


class test_EC2(TestCase):
    def setUp(self):
        self.ec2 = EC2()
        self.image_id = 'ami-00f8b1192da5566c5'  # amazon linux 2 in eu-west-1 (see test_amis for one in current region)  # todo: write helper class to find test amis

    def test__init__(self):
        assert type(self.ec2.client()  ).__name__ == 'EC2'
        assert type(self.ec2.resource()).__name__ == 'ec2.ServiceResource'

    def test_amis(self):
        owner       = 'amazon'
        name        = 'amzn2-ami-hvm-2.0.20180924-x86_64-ebs'
        description = 'Amazon Linux 2 AMI 2.0.20180924 x86_64 HVM ebs'
        result = self.ec2.amis(owner=owner, name=name, description=description)
        assert len(result) == 1
        assert result[0].get('Name') == name
        assert result[0].get('ImageId') == self.image_id       # 'ami-00f8b1192da5566c5'

    def test_create_instance(self):
        name              = 'osbot_aws.test_create_instance'
        tags              = {'an_name':'an_value', '2nd_name': '2nd value'}
        instance_type     = 't2.micro'
        kwargs = { 'name'           : name              ,
                   'instance_type'  : instance_type     ,
                   'tags'           : tags              }

        instance_id       = self.ec2.instance_create(self.image_id, **kwargs)             # todo: add tests with different instant_types
        instance_details  = self.ec2.instance_details(instance_id=instance_id)

        #instances_details = self.ec2.instances_details()
        #assert instances_details.get(instance_id) == instance_details                    # todo: deal with situation when the IP was set between executions

        assert list_index_by(instance_details.get('tags'), 'Key').keys().sorted() == ['2nd_name', 'Name', 'an_name']

        assert instance_details.get('cpus'          ) == 1
        assert instance_details.get('image_id'      ) == self.image_id
        assert instance_details.get('instance_type' ) == instance_type
        assert instance_details.get('state'         ) == {'Code': 0, 'Name': 'pending'}

        result_delete        = self.ec2.instance_delete(instance_id)
        terminating_instance = result_delete.get('TerminatingInstances')[0]

        assert terminating_instance.get('CurrentState') == {'Code': 32, 'Name': 'shutting-down'}
        assert terminating_instance.get('InstanceId'  ) == instance_id

    #def test_instance_details(self):
        # see test_create_instance

    def test_instances_details(self):
        result = self.ec2.instances_details()
        assert len(result) > 1

    def test_internet_gateway_create(self):
        tags                = {'Name': 'osbot_aws - test internet gateway'}
        internet_gateway_id  = self.ec2.internet_gateway_create(tags=tags).get('InternetGatewayId')

        assert self.ec2.internet_gateway_exists(internet_gateway_id) is True
        self.ec2.internet_gateway_delete(internet_gateway_id)
        assert self.ec2.internet_gateway_exists(internet_gateway_id) is False

    def test_internet_gateways(self):
        temp_vpc = Temp_VPC(add_internet_gateway=True)
        with temp_vpc:
            internet_gateway_id = temp_vpc.internet_gateway_id
            assert internet_gateway_id in self.ec2.internet_gateways(index_by='InternetGatewayId')

    def test_route_create(self):
        temp_vpc = Temp_VPC(add_route_table=True, add_internet_gateway=True)
        with temp_vpc:
            route_table_id      = temp_vpc.route_table_id
            internet_gateway_id = temp_vpc.internet_gateway_id
            route_table         = self.ec2.route_table(route_table_id=route_table_id)
            assert route_table.get('Routes').pop() == { 'DestinationCidrBlock': '0.0.0.0/0'         ,
                                                        'GatewayId'           : internet_gateway_id ,
                                                        'Origin'              : 'CreateRoute'       ,
                                                        'State'               : 'active'            }
    def test_route_table_associate(self):
        temp_vpc =Temp_VPC(add_route_table=True, add_subnet=True)
        with temp_vpc:
            route_table_id = temp_vpc.route_table_id
            subnet_id      = temp_vpc.subnet_id
            association_id = self.ec2.route_table_associate(route_table_id=route_table_id, subnet_id=subnet_id).get('AssociationId')
            route_table    = self.ec2.route_table(route_table_id)
            association    = route_table.get('Associations')[0]

            assert association.get('RouteTableId') == route_table_id
            assert association.get('SubnetId'    ) == subnet_id

            self.ec2.route_table_disassociate(association_id)
            route_table = self.ec2.route_table(route_table_id)
            assert route_table.get('Associations') == []


    def test_route_table_create(self):
        with Temp_VPC() as temp_vpc:
            vpc_id          = temp_vpc.vpc_id
            tags            = { 'Name': 'osbot_aws - test route table' }
            route_table_id  = self.ec2.route_table_create(vpc_id=vpc_id, tags=tags).get('RouteTableId')
            assert self.ec2.route_table_exists(route_table_id) is True
            self.ec2.route_table_delete(route_table_id)
            assert self.ec2.route_table_exists(route_table_id) is False

    def test_security_group(self):
        group_id = 'sg-050e49981ff7f1386'
        result = self.ec2.security_group(group_id)
        pprint(result)

    def test_security_group_create(self):
        group_name  = 'temp_security_group'
        description = 'testing security group creation'
        result      = self.ec2.security_group_create(group_name=group_name, description=description)
        group_id    = result.get('data').get('group_id')
        assert self.ec2.security_group_exists(group_id   = group_id  ) is True
        assert self.ec2.security_group_exists(group_name = group_name) is True
        assert self.ec2.security_group_delete(group_name = group_name) is True
        assert self.ec2.security_group_exists(group_id   = group_id  ) is False

    def test_security_groups(self):
        result = self.ec2.security_groups(index_by='GroupId')
        assert len(result) > 0

    def test_subnet_create(self):
        with Temp_VPC() as temp_vpc:
            vpc_id     = temp_vpc.vpc_id
            tags       = { 'Name': 'osbot_aws - test route table' }
            subnet_id  = self.ec2.subnet_create(vpc_id=vpc_id, tags=tags).get('SubnetId')
            assert self.ec2.subnet_exists(subnet_id) is True
            self.ec2.subnet_delete(subnet_id)
            assert self.ec2.subnet_exists(subnet_id) is False

    def test_subnets(self):
        result = self.ec2.subnets(index_by='SubnetId')
        assert len(result) > 0

    def test_vpc(self):
        vpc_id = self.ec2.vpcs_ids().pop()
        vpc    = self.ec2.vpc(vpc_id=vpc_id)
        assert vpc.get('VpcId') == vpc_id

    def test_vpc_attach_internet_gateway(self):
        tags                = {'Name': 'osbot_aws - test_vpc_attach_internet_gateway'}
        vpc_id              = self.ec2.vpc_create             (tags=tags).get('VpcId')
        internet_gateway_id = self.ec2.internet_gateway_create(tags=tags).get('InternetGatewayId')

        assert self.ec2.internet_gateway     (internet_gateway_id).get('Attachments') == []
        self.ec2.vpc_attach_internet_gateway (vpc_id=vpc_id,internet_gateway_id=internet_gateway_id)
        assert self.ec2.internet_gateway     (internet_gateway_id).get('Attachments') == [{'State': 'available', 'VpcId': vpc_id}]
        self.ec2.vpc_detach_internet_gateway (vpc_id=vpc_id, internet_gateway_id=internet_gateway_id)
        assert self.ec2.internet_gateway     (internet_gateway_id).get('Attachments') == []

        self.ec2.internet_gateway_delete(internet_gateway_id)
        self.ec2.vpc_delete             (vpc_id)

    def test_vpc_create(self):
        tags   = {'Name': 'osbot_aws - test_vpc_create'}
        vpc_id = self.ec2.vpc_create(tags=tags).get('VpcId')

        self.ec2.wait_for_vpc_available(vpc_id)
        assert self.ec2.vpc_exists(vpc_id) is True

        self.ec2.vpc_attribute_set(vpc_id, 'EnableDnsSupport'  , True)
        self.ec2.vpc_attribute_set(vpc_id, 'EnableDnsHostnames', True)
        self.ec2.vpc_delete(vpc_id)
        assert self.ec2.vpc_exists(vpc_id) is False

    def test_vpcs(self):
        result = self.ec2.vpcs(index_by='VpcId')
        assert len(result) > 0
        #pprint(result)

    @pytest.mark.skip('test can takes 30 to 50 secs to execute')                    # todo move to integration tests (where we can have longer running tests
    def test_wait_for_instance_running(self):                                       # todo create test that mocks the excution
        instance_id      = self.ec2.instance_create(self.image_id)
        instance_details = self.ec2.instance_details(instance_id)

        self.ec2.wait_for_instance_running(instance_id)

        assert instance_details.get('image_id') == self.image_id
        self.ec2.instance_delete(instance_id)

    @pytest.mark.skip('test takes 50sec to 4 minutes to execute')                   # todo: same as test_wait_for_instance_running
    def test_wait_for_instance_status_ok(self):                                     # todo see notes in test_wait_for_instance_running
        instance_id      = self.ec2.instance_create(self.image_id)
        instance_details = self.ec2.wait_for_instance_status_ok(instance_id)

        self.ec2.wait_for_instance_running(instance_id)                             # todo: add check for running state

        assert instance_details.get('image_id') == self.image_id
        self.ec2.instance_delete(instance_id)

