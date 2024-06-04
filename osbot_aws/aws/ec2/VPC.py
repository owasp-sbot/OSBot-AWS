from osbot_utils.decorators.methods.cache import cache
from osbot_utils.decorators.methods.cache_on_self import cache_on_self

from osbot_aws.apis.EC2 import EC2


class VPC:
    def __init__(self, vpc_name, tags):
        self.internet_gateway_id  = None
        self.route_table_id       = None
        self.security_group_id    = None
        self.subnet_id            = None
        self.vpc_id               = None
        self.vpc_name             = vpc_name
        self.tags                 = tags

    @cache_on_self
    def ec2(self):
        return EC2()

    def create_internet_gateway(self):
        self.internet_gateway_id = self.ec2().internet_gateway_create(tags=self.tags).get('InternetGatewayId')
        self.ec2().vpc_attach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)

    def create_route_table(self):
        self.route_table_id = self.ec2().route_table_create(vpc_id=self.vpc_id, tags=self.tags).get('RouteTableId')

    def create_security_group(self):
        security_group_name    = self.vpc_name
        description            = self.vpc_name
        result                 = self.security_group_id = self.ec2().security_group_create(security_group_name=security_group_name, description=description, vpc_id=self.vpc_id,tags=self.tags)
        self.security_group_id = result.get('data').get('security_group_id')

    def create_subnet(self):
        self.subnet_id = self.ec2().subnet_create(vpc_id=self.vpc_id, tags=self.tags).get('SubnetId')

    def create_vpc(self):
        self.vpc_id = self.ec2().vpc_create(tags=self.tags).get('VpcId')

    def delete_internet_gateway(self):
        self.ec2().vpc_detach_internet_gateway(vpc_id=self.vpc_id, internet_gateway_id=self.internet_gateway_id)
        self.ec2().internet_gateway_delete(self.internet_gateway_id)

    def delete_security_group(self):
        self.ec2().security_group_delete(self.security_group_id)

    def delete_subnet(self):
        self.ec2().subnet_delete(self.subnet_id)

    def delete_route_table(self):
        self.ec2().route_table_delete(self.route_table_id)

    def delete_vpc(self):
        self.ec2().vpc_delete(self.vpc_id)