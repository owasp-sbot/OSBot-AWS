import boto3

from osbot_aws.apis.Session import Session


class Ec2:
    def __init__(self):
        self.ec2          = Session().client('ec2')
        self.ec2_resource = boto3.resource('ec2')



    def instances_details(self):
        instances = {}
        for instance in self.ec2_resource.instances.all():
            instance_id = instance.instance_id
            instances[instance_id] = { 'cpus'         : instance.cpu_options['CoreCount']     ,
                                       'image_id'     : instance.image_id                     ,
                                       'instance_type': instance.instance_type                ,
                                       'public_ip'    : instance.public_ip_address            ,
                                       'state'        : instance.state                        ,
                                       'tags'         : instance.tags                         }

        return instances

    def security_groups(self):
        groups={}
        for group in self.ec2.describe_security_groups().get('SecurityGroups'):
            groups[group.get('GroupId')] = group
        return groups

    def subnets(self):
        subnets = {}
        for subnet in self.ec2.describe_subnets().get('Subnets'):
            subnets[subnet.get('SubnetId')] = subnet
        return subnets

    def vpcs(self):
        vpcs = {}
        for vpc in self.ec2.describe_vpcs().get('Vpcs'):
            vpcs[vpc.get('VpcId')] = vpc
        return vpcs