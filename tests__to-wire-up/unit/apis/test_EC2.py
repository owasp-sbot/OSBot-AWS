import pytest

from osbot_aws.aws.iam.STS import STS
from osbot_utils.utils.Lists import list_index_by

from osbot_utils.utils.Files import file_exists, file_contents, file_delete

from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC
from osbot_aws.apis.EC2                   import EC2
from unittest                             import TestCase
from osbot_utils.utils.Dev                import pprint


class test_EC2(TestCase):
    def setUp(self):
        self.ec2 = EC2()
        self.image_id = 'ami-00f8b1192da5566c5'  # amazon linux 2 in eu-west-1
        #self.image_id = 'ami-074882b79a16e2e6e'  # amazon linux 2 in eu-west-2  # todo: write helper class to find test amis


    def test__init__(self):
        assert type(self.ec2.client()  ).__name__ == 'EC2'
        assert type(self.ec2.resource()).__name__ == 'ec2.ServiceResource'

    def test_amis(self):                                                       # todo check the performance of the amis and if there is more efficient way to get this data (this test takes 5 seconds to execute)
        owner       = 'amazon'
        name        = 'amzn2-ami-hvm-2.0.20180924-x86_64-ebs'
        description = 'Amazon Linux 2 AMI 2.0.20180924 x86_64 HVM ebs'
        result = self.ec2.amis(owner=owner, name=name, description=description)
        assert len(result) == 1
        assert result[0].get('Name') == name
        assert result[0].get('ImageId') == self.image_id

        # result = self.ec2.amis(owner=owner, name='amzn*', index_by='Name')
        # pprint(len(result))
        # pprint(result)

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

        terminating_instance        = self.ec2.instance_delete(instance_id)
        #terminating_instance = result_delete.get('TerminatingInstances')[0]

        assert terminating_instance.get('CurrentState') == {'Code': 32, 'Name': 'shutting-down'}
        assert terminating_instance.get('InstanceId'  ) == instance_id

    #def test_instance_details(self):
        # see test_create_instance

    def test_instances_details(self):
        result = self.ec2.instances_details()
        assert len(result) > 1

    def test_instances_details__with_filter(self):
        filter = [{"Name": "instance-state-name", "Values":["running"]}]
        result = self.ec2.instances_details(filters=filter)                 # todo: add test for passing array
        for key, instance in result.items():
            assert instance.get('state').get('Name') == 'running'


    def test_internet_gateway_create(self):
        tags                = {'Name': 'osbot_aws - test internet gateway'}
        internet_gateway_id  = self.ec2.internet_gateway_create(tags=tags).get('InternetGatewayId')

        assert self.ec2.internet_gateway_exists(internet_gateway_id) is True
        self.ec2.internet_gateway_delete(internet_gateway_id)
        assert self.ec2.internet_gateway_exists(internet_gateway_id) is False

    def test_internet_gateways(self):
        temp_vpc = Temp_VPC(add_internet_gateway=True)
        with temp_vpc:
            internet_gateway_id = temp_vpc.vpc.internet_gateway_id
            assert internet_gateway_id in self.ec2.internet_gateways(index_by='InternetGatewayId')

    def test_key_pair_create(self):
        key_name     = 'osbot-unit-tests-temp_key_pair'
        tags         = { 'Name': key_name }
        result       = self.ec2.key_pair_create(key_name=key_name, tags=tags)
        key_pair_id  = result.get('KeyPairId')
        assert self.ec2.key_pair_exists(key_pair_id   = key_pair_id  ) is True
        assert self.ec2.key_pair_exists(key_pair_name = key_name     ) is True
        assert self.ec2.key_pair_delete(key_pair_name = key_name     ) is True
        assert self.ec2.key_pair_exists(key_pair_id   = key_pair_id  ) is False

    def test_key_pair_create_to_file(self):
        key_name      = 'osbot-unit-tests-temp_key_pair'
        result        = self.ec2.key_pair_create_to_file(key_name=key_name)
        key_pair_id   = result.get('key_pair').get('KeyPairId')
        path_key_pair = result.get('path_key_pair')

        assert file_exists(path_key_pair)                                   is True
        assert file_contents(path_key_pair).find('BEGIN RSA PRIVATE KEY')    > -1
        assert self.ec2.key_pair_delete(key_pair_id = key_pair_id)          is True
        assert file_delete(path_key_pair)                                   is True


    def test_route_create(self):
        temp_vpc = Temp_VPC(add_route_table=True, add_internet_gateway=True)
        with temp_vpc:
            route_table_id      = temp_vpc.vpc.route_table_id
            internet_gateway_id = temp_vpc.vpc.internet_gateway_id
            self.ec2.route_create(route_table_id=route_table_id,internet_gateway_id=internet_gateway_id)
            route_table         = self.ec2.route_table(route_table_id=route_table_id)
            assert route_table.get('Routes').pop() == { 'DestinationCidrBlock': '0.0.0.0/0'         ,
                                                        'GatewayId'           : internet_gateway_id ,
                                                        'Origin'              : 'CreateRoute'       ,
                                                        'State'               : 'active'            }
    def test_route_table_associate(self):
        temp_vpc =Temp_VPC(add_route_table=True, add_subnet=True)
        with temp_vpc:
            route_table_id = temp_vpc.vpc.route_table_id
            subnet_id      = temp_vpc.vpc.subnet_id
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
            vpc_id          = temp_vpc.vpc.vpc_id
            tags            = { 'Name': 'osbot_aws - test route table' }
            route_table_id  = self.ec2.route_table_create(vpc_id=vpc_id, tags=tags).get('RouteTableId')
            assert self.ec2.route_table_exists(route_table_id) is True
            self.ec2.route_table_delete(route_table_id)
            assert self.ec2.route_table_exists(route_table_id) is False

    # def test_security_group(self):
    #     pass

    def test_security_group_authorize_ingress(self):
        security_group_name  = 'SSH-ONLY'
        description          = 'only allow SSH traffic'
        port                 = 22
        account_id           = STS().current_account_id()
        with Temp_VPC() as temp_vpc:
            vpc_id            = temp_vpc.vpc.pc_id
            security_group_id = self.ec2.security_group_create(security_group_name=security_group_name, description=description, vpc_id=vpc_id).get('data').get('security_group_id')

            self.ec2.security_group_authorize_ingress(security_group_id=security_group_id, port=port)

            security_group    = self.ec2.security_group(security_group_id)
            assert security_group == {    'Description': description        ,
                                          'GroupId'    : security_group_id  ,
                                          'GroupName'  : security_group_name,
                                          'IpPermissions': [ { 'FromPort'        : port                     ,
                                                               'IpProtocol'      : 'tcp'                    ,
                                                               'IpRanges'        : [{'CidrIp': '0.0.0.0/0'}],
                                                               'Ipv6Ranges'      : []                       ,
                                                               'PrefixListIds'   : []                       ,
                                                               'ToPort'          : port                     ,
                                                               'UserIdGroupPairs': []}]                     ,
                                          'IpPermissionsEgress': [ { 'IpProtocol'      : '-1'                     ,
                                                                     'IpRanges'        : [{'CidrIp': '0.0.0.0/0'}],
                                                                     'Ipv6Ranges'      : []                       ,
                                                                     'PrefixListIds'   : []                       ,
                                                                     'UserIdGroupPairs': []}]                     ,
                                          'OwnerId': account_id ,
                                          'VpcId'  : vpc_id     }
            assert self.ec2.security_group_delete(security_group_id) is True

    def test_security_group_create(self):
        security_group_name  = 'temp_security_group'
        description          = 'testing security group creation'
        result               = self.ec2.security_group_create(security_group_name=security_group_name, description=description)
        security_group_id = result.get('data').get('security_group_id')
        assert self.ec2.security_group_exists(security_group_id   = security_group_id  ) is True
        assert self.ec2.security_group_exists(security_group_name = security_group_name) is True
        assert self.ec2.security_group_delete(security_group_name = security_group_name) is True
        assert self.ec2.security_group_exists(security_group_id   = security_group_id  ) is False

    def test_security_group_default(self):
        pprint(self.ec2.security_group_default())

    def test_security_groups(self):
        result = self.ec2.security_groups(index_by='GroupId')
        assert len(result) > 0
        pprint(result)

    def test_subnet_create(self):
        with Temp_VPC() as temp_vpc:
            vpc_id     = temp_vpc.vpc.vpc_id
            tags       = { 'Name': 'osbot_aws - test route table' }
            subnet_id  = self.ec2.subnet_create(vpc_id=vpc_id, tags=tags).get('SubnetId')
            assert self.ec2.subnet_exists(subnet_id) is True
            self.ec2.subnet_delete(subnet_id)
            assert self.ec2.subnet_exists(subnet_id) is False

    def test_subnet_default_for_az(self):
        result = self.ec2.subnet_default_for_az()
        pprint(result)

    def test_subnets(self):
        result = self.ec2.subnets(index_by='SubnetId')
        assert len(result) > 0
        #pprint(result)

    def test_subnets_default_for_az(self):
        result = self.ec2.subnets_default_for_az()
        assert len(result) == 3                         # in most regions I believe this should be set to 3

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

    def test_vpc_default(self):
        pprint(self.ec2.vpc_default())

    def test_vpcs(self):
        result = self.ec2.vpcs(index_by='VpcId')
        assert len(result) > 0
        pprint(result)

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

