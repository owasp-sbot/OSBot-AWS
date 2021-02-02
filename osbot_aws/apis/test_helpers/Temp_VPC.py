from osbot_utils.utils.Misc import random_string

from osbot_aws.apis.EC2 import EC2


class Temp_VPC:
    def __init__(self, add_internet_gateway=False, add_route_table=False, add_security_group=False, add_subnet=False):
        self.add_internet_gateway = add_internet_gateway
        self.add_route_table      = add_route_table
        self.add_security_group   = add_security_group
        self.add_subnet           = add_subnet
        self.ec2                  = EC2()
        self.vpc_name             = random_string(prefix='osbot_aws-temp_vpc-')
        self.tags                 = {'Name': self.vpc_name}
        self.internet_gateway_id  = None
        self.route_table_id       = None
        self.security_group_id    = None
        self.subnet_id            = None
        self.vpc_id               = None

    def __enter__(self):
        self.create_vpc()
        self.create_route_table()
        self.create_internet_gateway()
        self.create_security_group()
        self.create_subnet()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.delete_internet_gateway()
        self.delete_route_table()
        self.delete_security_group()
        self.delete_subnet()
        self.delete_vpc()

    def create_internet_gateway(self):
        if self.add_internet_gateway:
            self.internet_gateway_id = self.ec2.internet_gateway_create(tags=self.tags).get('InternetGatewayId')
            self.ec2.vpc_attach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)

    def create_route_table(self):
        if self.add_route_table:
            self.route_table_id = self.ec2.route_table_create(vpc_id=self.vpc_id, tags=self.tags).get('RouteTableId')

    def create_security_group(self):
        if self.add_security_group:
            security_group_name    = self.vpc_name
            description            = self.vpc_name
            result                 = self.security_group_id = self.ec2.security_group_create(security_group_name=security_group_name, description=description, vpc_id=self.vpc_id)
            self.security_group_id = result.get('data').get('security_group_id')

    def create_subnet(self):
        if self.add_subnet:
            self.subnet_id = self.ec2.subnet_create(vpc_id=self.vpc_id, tags=self.tags).get('SubnetId')

    def create_vpc(self):
        self.vpc_id = self.ec2.vpc_create(tags=self.tags).get('VpcId')

    def delete_internet_gateway(self):
        if self.add_internet_gateway:
            self.ec2.vpc_detach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)
            self.ec2.internet_gateway_delete(self.internet_gateway_id)

    def delete_security_group(self):
        if self.add_security_group:
            self.ec2.security_group_delete(self.security_group_id)

    def delete_subnet(self):
        if self.add_subnet:
            self.ec2.subnet_delete(self.subnet_id)

    def delete_route_table(self):
        if self.add_route_table:
            self.ec2.route_table_delete(self.route_table_id)

    def delete_vpc(self):
        self.ec2.vpc_delete(self.vpc_id)
