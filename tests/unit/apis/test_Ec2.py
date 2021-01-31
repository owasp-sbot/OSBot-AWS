import sys ;

import pytest

from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.utils.Misc import list_set, list_group_by, list_index_by

sys.path.append('..')

from osbot_aws.apis.Ec2 import Ec2
from unittest import TestCase
from osbot_utils.utils.Dev import Dev, pprint


class test_Ec2(TestCase):
    def setUp(self):
        self.ec2 = Ec2()
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

    def test_security_groups(self):
        result = self.ec2.security_groups()
        assert len(result) > 0

    def test_subnets(self):
        result = self.ec2.subnets()
        assert len(result) > 0

    def test_vpcs(self):
        result = self.ec2.vpcs()
        assert len(result) > 0

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

