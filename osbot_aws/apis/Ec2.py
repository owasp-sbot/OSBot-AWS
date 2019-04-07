import boto3


class Ec2:
    def __init__(self):
        self.ec2 = boto3.client('ec2')

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