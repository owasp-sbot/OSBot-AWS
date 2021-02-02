from osbot_utils.utils.Misc import random_string

from osbot_aws.apis.EC2 import EC2


class Temp_VPC:
    def __init__(self, add_internet_gateway=True):
        self.add_internet_gateway = add_internet_gateway
        self.ec2                  = EC2()
        self.vpc_name             = random_string(prefix='osbot_aws-temp_vpc-')
        self.tags                 = {'Name': self.vpc_name}
        self.internet_gateway_id  = None
        self.vpc_id               = None

    def __enter__(self):
        self.create_vpc()
        self.create_internet_gateway()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.delete_internet_gateway()
        self.delete_vpc()

    def create_internet_gateway(self):
        if self.add_internet_gateway:
            self.internet_gateway_id = self.ec2.internet_gateway_create(tags=self.tags).get('InternetGatewayId')
            self.ec2.vpc_attach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)

    def create_vpc(self):
        self.vpc_id = self.ec2.vpc_create(tags=self.tags).get('VpcId')

    def delete_internet_gateway(self):
        if self.add_internet_gateway:
            self.ec2.vpc_detach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)
            self.ec2.internet_gateway_delete(self.internet_gateway_id)

    def delete_vpc(self):
        self.ec2.vpc_delete(self.vpc_id)
