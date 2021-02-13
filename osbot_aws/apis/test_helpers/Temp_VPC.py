from osbot_aws.helpers.VPC import VPC
from osbot_utils.utils.Misc import random_string

from osbot_aws.apis.EC2 import EC2


class Temp_VPC:
    def __init__(self, add_internet_gateway=False, add_route_table=False, add_security_group=False, add_subnet=False):
        self.add_internet_gateway = add_internet_gateway
        self.add_route_table      = add_route_table
        self.add_security_group   = add_security_group
        self.add_subnet           = add_subnet
        self.vpc_name             = random_string(prefix='osbot_aws-temp_vpc-')
        self.tags                 = {'Name': self.vpc_name}
        self.vpc                  = VPC(vpc_name=self.vpc_name, tags=self.tags)


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
            self.vpc.create_internet_gateway()
        return self

    def create_route_table(self):
        if self.add_route_table:
            self.vpc.create_route_table()
        return self

    def create_security_group(self):
        if self.add_security_group:
            self.vpc.create_security_group()
        return self

    def create_subnet(self):
        if self.add_subnet:
            self.vpc.create_subnet()
        return self

    def create_vpc(self):
        self.vpc.create_vpc()
        return self

    def delete_internet_gateway(self):
        if self.add_internet_gateway:
            self.vpc.delete_internet_gateway()
        return self

    def delete_security_group(self):
        if self.add_security_group:
            self.vpc.delete_security_group()
        return self

    def delete_subnet(self):
        if self.add_subnet:
            self.vpc.delete_subnet()
        return self

    def delete_route_table(self):
        if self.add_route_table:
            self.vpc.delete_route_table()
        return self

    def delete_vpc(self):
        self.vpc.delete_vpc()
        return self
