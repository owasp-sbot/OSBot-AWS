from unittest import TestCase

import pytest

from k8_kubernetes.kubernetes.Ssh import Ssh
from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC
from osbot_aws.helpers.AMI import AMI
from osbot_utils.utils.Misc import random_string, wait

from osbot_aws.apis.EC2 import EC2
from osbot_utils.utils.Dev import pprint, print_now


class test_EC2_Create_Instance(TestCase):

    def setUp(self) -> None:
        self.ec2 = EC2()

    #def test_queue(self):
    #    Queue

    def test_create_and_delete_ec2_instance(self):
        image_id = AMI().amazon_linux_2()
        name     = random_string(prefix='test_ec2_with_ssh_support-')
        tags     = {'Name': f'osbot_aws - {name}'}
        kwargs   = {  "image_id"         : image_id          ,
                      "name"             : name              ,
                      "tags"             : tags              }

        instance_id = self.ec2.instance_create(**kwargs)
        assert self.ec2.instance_details(instance_id=instance_id).get('state') ==  {'Code': 0, 'Name': 'pending'}
        self.ec2.instance_delete(instance_id)
        assert self.ec2.instance_details(instance_id=instance_id).get('state') == {'Code': 32, 'Name': 'shutting-down'}


    @pytest.mark.skip('todo: see why test below was failing with exception: botocore.exceptions.WaiterError: Waiter InstanceTerminated failed: Waiter encountered a terminal failure state: For expression "Reservations[].Instances[].State.Name" we matched expected path: "pending" at least once')
    def test_ec2_with_ssh_support(self):
        import logging
        #logging.getLogger('botocore').setLevel(logging.DEBUG)
        #logging.getLogger('boto3').setLevel(logging.DEBUG)
        image_id            = AMI().amazon_linux_2()
        name                = random_string(prefix='test_ec2_with_ssh_support-')
        tags                = {'Name': f'osbot_aws - {name}'}
        key_name            = f'osbot-{name}'
        allow_port          = 22

        key_pair            = self.ec2.key_pair_create_to_file(key_name=key_name)
        key_pair_id         = key_pair.get('key_pair_id'  )
        path_key_pair       = key_pair.get('path_key_pair')


        temp_vpc = Temp_VPC(add_security_group=True, add_subnet=True,add_internet_gateway=True,add_route_table=True)

        with temp_vpc:
            vpc_id              = temp_vpc.vpc.vpc_id
            internet_gateway_id = temp_vpc.vpc.internet_gateway_id
            security_group_id   = temp_vpc.vpc.security_group_id
            subnet_id           = temp_vpc.vpc.subnet_id
            route_table_id      = temp_vpc.vpc.route_table_id

            # self.ec2.vpc_attribute_set               (vpc_id, 'EnableDnsSupport'  , True)
            # self.ec2.vpc_attribute_set               (vpc_id, 'EnableDnsHostnames', True)
            # self.ec2.route_create                    (route_table_id    = route_table_id    , internet_gateway_id = internet_gateway_id)
            # self.ec2.route_table_associate           (route_table_id    = route_table_id    , subnet_id           = subnet_id          )
            # self.ec2.security_group_authorize_ingress(security_group_id = security_group_id , port                = allow_port         )

            network_interface = {'SubnetId'                : subnet_id,
                                 'DeviceIndex'             : 0        ,
                                 'AssociatePublicIpAddress': True     ,
                                 'Groups'                  : [security_group_id]}

            kwargs = {  "image_id"         : image_id          ,
                        "key_name"         : key_name          ,
                        "name"             : name              ,
                        "network_interface": network_interface ,
                        "tags"             : tags              }

            instance_id = self.ec2.instance_create(**kwargs)

            print_now()
            pprint(self.ec2.instance_details(instance_id=instance_id))
            #self.ec2.wait_for_instance_exists(instance_id=instance_id)

            # # print_now()
            # # pprint(self.ec2.instance_details(instance_id=instance_id))
            # # self.ec2.wait_for_instance_running(instance_id=instance_id)
            # #
            # # print_now()
            # # pprint(self.ec2.instance_details(instance_id=instance_id))
            # # self.ec2.wait_for_instance_status_ok(instance_id=instance_id)
            #
            instance_id = self.ec2.instance_delete(instance_id)
            # print_now()
            # pprint(self.ec2.instance_details(instance_id=instance_id))
            #
            # this was throwing error "botocore.exceptions.WaiterError: Waiter InstanceTerminated failed: Waiter encountered a terminal failure state: For expression "Reservations[].Instances[].State.Name" we matched expected path: "pending" at least once"
            self.ec2.wait_for_instance_terminated(instance_id=instance_id)
            #
            print_now()
            pprint(self.ec2.instance_details(instance_id=instance_id))

        assert self.ec2.key_pair_delete(key_pair_id=key_pair_id) is True

    def test_connect_to_ec2_instance(self):

        path_to_key = '/var/folders/_j/frqs70d93l328f307rw2jx5h0000gn/T/tmp8_tl8q5l/osbot-test_ec2_with_ssh_supporteyvjpbqb.pem'
        username    = 'ec2-user'
        server_ip   = "3.251.63.86"
        ssh_config = {"server": server_ip,
                      "ssh_key": path_to_key,
                      "user": username}
        result = Ssh(ssh_config=ssh_config).ls('/')
        pprint(result)