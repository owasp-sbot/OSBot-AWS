from unittest import TestCase

from k8_kubernetes.kubernetes.Ssh import Ssh
from osbot_utils.utils.Misc import random_string

from osbot_aws.apis.EC2 import EC2
from osbot_aws.apis.test_helpers.Temp_VPC import Temp_VPC
from osbot_utils.utils.Dev import pprint


class test_Create_EC2_Instances(TestCase):

    def setUp(self) -> None:
        self.ec2 = EC2()

    def test_ec2_with_ssh_support(self):
        image_id            = 'ami-00f8b1192da5566c5'  # amazon linux 2 in eu-west-1
        name                = random_string(prefix='test_ec2_with_ssh_support')
        tags                = {'Name': f'osbot_aws - {name}'}
        key_name            = f'osbot-{name}'
        allow_port          = 22

        key_pair      = self.ec2.key_pair_create_to_file(key_name=key_name)
        key_pair_id   = key_pair.get('key_pair_id'  )
        path_key_pair = key_pair.get('path_key_pair')

        temp_vpc = Temp_VPC(add_security_group=True, add_subnet=True,add_internet_gateway=True,add_route_table=True)

        with temp_vpc:
            vpc_id              = temp_vpc.vpc_id
            internet_gateway_id = temp_vpc.internet_gateway_id
            security_group_id   = temp_vpc.security_group_id
            subnet_id           = temp_vpc.subnet_id
            route_table_id      = temp_vpc.route_table_id

            self.ec2.vpc_attribute_set               (vpc_id, 'EnableDnsSupport'  , True)
            self.ec2.vpc_attribute_set               (vpc_id, 'EnableDnsHostnames', True)
            self.ec2.route_create                    (route_table_id    = route_table_id    , internet_gateway_id = internet_gateway_id)
            self.ec2.route_table_associate           (route_table_id    = route_table_id    , subnet_id           = subnet_id          )
            self.ec2.security_group_authorize_ingress(security_group_id = security_group_id , port                = allow_port         )

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

            #self.ec2.wait_for_instance_running(instance_id=instance_id)

            instance =  self.ec2.instance_details(instance_id=instance_id)

            pprint(instance)

            self.ec2.instance_delete(instance_id=instance_id)

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