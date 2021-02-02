from os import chmod

import boto3
from botocore.exceptions import ClientError
from osbot_utils.utils.Files import file_name, temp_folder, path_combine, file_create

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache import cache
from osbot_aws.apis.Session import Session
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Status import status_warning, status_ok


class EC2:

    @cache
    def client(self):
        return Session().client('ec2')
    @cache
    def resource(self):
        return Session().resource('ec2')

    def amis(self, owner='self', state='available', name=None, description=None):  # todo: find how to search for amis in the quick start
        kwargs = {'Owners' : [owner] ,
                  'Filters' : [ {'Name': 'state', 'Values': [state]}]}

        if name       : kwargs.get('Filters').append({'Name': 'name'       , 'Values': [name]})
        if description: kwargs.get('Filters').append({'Name': 'description', 'Values': [description]})

        return self.client().describe_images(**kwargs).get('Images')

    def instance_create(self, image_id, name='created by osbot_aws', instance_type='t2.micro', iam_instance_profile=None, key_name=None, network_interface=None, tags=None,):
        kwargs = {  "ImageId"      : image_id                                                               ,
                    "InstanceType" : instance_type                                                          ,
                    "MaxCount"     : 1                                                                      ,
                    "MinCount"     : 1                                                                      ,
                    'TagSpecifications': self.tag_specifications_create(tags=tags, name=name,resource_type='instance')}

        if iam_instance_profile : kwargs["IamInstanceProfile"] = iam_instance_profile
        if key_name             : kwargs["KeyName"           ] = key_name
        if network_interface    : kwargs['NetworkInterfaces' ] = [network_interface]

        result   = self.client().run_instances(**kwargs)
        instance = result.get('Instances')[0]
        return  instance.get('InstanceId')

    def format_instance_details(self, target):
        if target:
            return { 'cpus'         : target.cpu_options['CoreCount']     ,
                     'image_id'     : target.image_id                     ,
                     'instance_type': target.instance_type                ,
                     'public_ip'    : target.public_ip_address            ,
                     'state'        : target.state                        ,
                     'tags'         : target.tags                         }
        return {}

    def instance_details(self, instance_id=None, filter=None):
        kwargs = { }
        if instance_id: kwargs['InstanceIds'] = [instance_id]
        result = self.resource().instances.filter(**kwargs)             # todo see client().describe_instances is a better method to use
        for instance in result:
            return self.format_instance_details(instance)

    def instance_delete(self, instance_id):
        return self.client().terminate_instances(InstanceIds=[instance_id])

    def instances_details(self):
        instances = {}
        for instance in self.resource().instances.all():
            instance_id = instance.instance_id
            instances[instance_id] = self.format_instance_details(instance)
        return instances

    def internet_gateway(self, internet_gateway_id):
        result = self.internet_gateways(internet_gateways_ids=[internet_gateway_id])
        if len(result) == 1:
            return result[0]

    def internet_gateway_create(self, tags=None):
        kwargs = { 'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='internet-gateway') }
        return self.client().create_internet_gateway(**kwargs).get('InternetGateway')

    def internet_gateway_delete(self, internet_gateway_id):
        return self.client().delete_internet_gateway(InternetGatewayId=internet_gateway_id)

    def internet_gateway_exists(self, internet_gateway_id):
        return self.internet_gateway(internet_gateway_id) is not None

    @index_by
    @group_by
    def internet_gateways(self, internet_gateways_ids=None):                         # todo: refactor this entire internet_gateways and (for example) vpns, since they have mostly the same code and there is a number of helper methods added for each of them
        kwargs = {}
        if internet_gateways_ids:
            kwargs['InternetGatewayIds'] = internet_gateways_ids
        try:
            return self.client().describe_internet_gateways(**kwargs).get('InternetGateways')
        except ClientError as e:                                                    # todo: refactor this pattern into a helper with statement (which receives as param the Error.Code value
            if e.response.get('Error', {}).get('Code') == 'InvalidInternetGatewayID.NotFound':
                return []
            raise

    def key_pair(self, key_pair_id=None, key_pair_name=None):
        if key_pair_id:
            return self.key_pairs(index_by="KeyPairId").get(key_pair_id)
        if key_pair_name:
            return self.key_pairs(index_by="KeyName"  ).get(key_pair_name)

    @remove_return_value(field_name='ResponseMetadata')
    def key_pair_create(self, key_name, tags=None):
        kwargs = {'KeyName'          : key_name                                                           ,
                  'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='key-pair')}

        return self.client().create_key_pair(**kwargs)

    def key_pair_create_to_file(self, key_name, target_folder=None, tags=None):
        key_pair          = self.key_pair_create(key_name=key_name,tags=tags)
        key_pair_id       = key_pair.get('KeyPairId')
        key_pair_material = key_pair.get('KeyMaterial')

        if target_folder is None:
            target_folder = temp_folder()
        path_key_pair = path_combine(target_folder, key_name + ".pem")
        file_create(path_key_pair,key_pair_material)
        chmod(path_key_pair, 0o400)
        return {'path_key_pair':path_key_pair, 'key_pair_id':key_pair_id, 'key_pair':key_pair}

    def key_pair_delete(self, key_pair_id=None, key_pair_name=None):
        if key_pair_id:
            self.client().delete_key_pair(KeyPairId=key_pair_id)
        if key_pair_name:
            self.client().delete_key_pair(KeyName=key_pair_name)
        return self.key_pair_exists(key_pair_id=key_pair_id, key_pair_name=key_pair_name) is False

    def key_pair_exists(self, key_pair_id=None, key_pair_name=None):
        return self.key_pair(key_pair_id=key_pair_id, key_pair_name=key_pair_name) is not None

    @index_by
    @group_by
    def key_pairs(self):
        return self.client().describe_key_pairs().get('KeyPairs')

    def route_create(self, route_table_id, internet_gateway_id, destination_cidr_block='0.0.0.0/0'):
        kwargs = { "DestinationCidrBlock": destination_cidr_block ,
                   "GatewayId"           : internet_gateway_id    ,
                   "RouteTableId"        : route_table_id         }
        return self.client().create_route(**kwargs)

    def route_table(self, route_table_id):
        result = self.route_tables(route_tables_ids=[route_table_id])
        if result and len(result) == 1:
            return result[0]

    @remove_return_value(field_name='ResponseMetadata')
    def route_table_associate(self, route_table_id, subnet_id=None, gateway_id=None):
        kwargs = { 'RouteTableId' : route_table_id}
        if subnet_id:
            kwargs['SubnetId'] = subnet_id
        if gateway_id:
            kwargs['GatewayId'] = gateway_id
        return self.client().associate_route_table(**kwargs)

    def route_table_create(self, vpc_id, tags=None):
        kwargs = { 'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='route-table'),
                   'VpcId'            : vpc_id }
        result = self.client().create_route_table(**kwargs)
        return result.get('RouteTable')

    def route_table_delete(self, route_table_id):
        return self.client().delete_route_table(RouteTableId=route_table_id)

    def route_table_disassociate(self, association_id):
        return self.client().disassociate_route_table(AssociationId=association_id)

    def route_table_exists(self, route_table_id):
        return self.route_table(route_table_id) is not None

    @index_by
    @group_by
    def route_tables(self, route_tables_ids=None):                         # todo: refactor this entire route_tables and (for example) vpns, since they have mostly the same code and there is a number of helper methods added for each of them
        kwargs = {}
        if route_tables_ids:
            kwargs['RouteTableIds'] = route_tables_ids
        try:
            return self.client().describe_route_tables(**kwargs).get('RouteTables')
        except ClientError as e:                                                    # todo: refactor this pattern into a helper with statement (which receives as param the Error.Code value
            if e.response.get('Error', {}).get('Code') == 'InvalidRouteTableID.NotFound':
                return []
            raise

    def security_group(self, security_group_id=None, security_group_name=None):
        if security_group_id:
            return self.security_groups(index_by="GroupId"  ).get(security_group_id)
        if security_group_name:
            return self.security_groups(index_by="GroupName").get(security_group_name)

    def security_group_authorize_ingress(self, security_group_id, port=None, from_port=None, to_port=None, cidr_ip='0.0.0.0/0', ip_protocol='tcp'):
        if port:
            from_port = port
            to_port   = port

        kwargs = { "CidrIp"     : cidr_ip           ,
                   "IpProtocol" : ip_protocol       ,
                   'GroupId'    : security_group_id ,
                   "FromPort"   : from_port         ,
                   "ToPort"     : to_port           }

        return self.client().authorize_security_group_ingress(**kwargs)


    def security_group_create(self, security_group_name, description, vpc_id=None, tags=None):
        if self.security_group_exists(security_group_name=security_group_name):
            security_group_id =  self.security_group(security_group_name=security_group_name).get('GroupId')            # todo see what is a better way to implement this workflow, since at the moment there are two full calls to the self.security_groups() method
            return status_warning(message=f'Security group already existed: {security_group_name}' , data= { 'security_group_id':security_group_id })
        kwargs = { 'Description'      : description                                                               ,
                   'GroupName'        : security_group_name                                                       ,
                   'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='security-group') }
        if vpc_id:
            kwargs['VpcId'] = vpc_id

        security_group_id = self.client().create_security_group(**kwargs).get('GroupId')
        return status_ok(message=f'Security group created ok: {security_group_name}', data= { 'security_group_id': security_group_id })

    def security_group_delete(self, security_group_id=None, security_group_name=None):
        if security_group_id:
            self.client().delete_security_group(GroupId=security_group_id)
        if security_group_name:
            self.client().delete_security_group(GroupName=security_group_name)
        return self.security_group_exists(security_group_id=security_group_id, security_group_name=security_group_name) is False

    def security_group_exists(self, security_group_id=None, security_group_name=None):
        return self.security_group(security_group_id=security_group_id, security_group_name=security_group_name) is not None

    @index_by
    @group_by
    def security_groups(self):
        return self.client().describe_security_groups().get('SecurityGroups')

    def subnet(self, subnet_id):
        result = self.subnets(subnets_ids=[subnet_id])
        if result and len(result) == 1:
            return result[0]

    def subnet_create(self, vpc_id, cidr_block='172.16.1.0/24', tags=None):
        kwargs = { 'CidrBlock'        : cidr_block                                                       ,
                   'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='subnet'),
                   'VpcId'            : vpc_id                                                           }
        result = self.client().create_subnet(**kwargs)
        return result.get('Subnet')

    def subnet_delete(self, subnet_id):
        return self.client().delete_subnet(SubnetId=subnet_id)

    def subnet_exists(self, subnet_id):
        return self.subnet(subnet_id) is not None

    @index_by
    @group_by
    def subnets(self, subnets_ids=None):
        kwargs = {}
        if subnets_ids:
            kwargs['SubnetIds'] = subnets_ids
        try:
            return self.client().describe_subnets(**kwargs).get('Subnets')
        except ClientError as e:                                                    # todo: refactor this pattern into a helper with statement (which receives as param the Error.Code value
            if e.response.get('Error', {}).get('Code') == 'InvalidSubnetID.NotFound':
                return []
            raise

    def tag_specifications_create(self, tags=None, name=None, resource_type=None):
        data =  []
        if name:
            if tags:
                tags['Name'] = name
            else:
                tags = { 'Name': name }
        if tags:
            tag_specification = { 'Tags': [] }
            if resource_type:
                tag_specification['ResourceType'] = resource_type
            for key,value in tags.items():
                tag_specification['Tags'].append({'Key':key, 'Value':value})
            data.append(tag_specification)
        return data

    def vpc(self, vpc_id):
        result = self.vpcs(vpcs_ids=[vpc_id])
        if len(result) == 1:
            return result[0]

    def vpc_attach_internet_gateway(self, vpc_id, internet_gateway_id):
        return self.client().attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=internet_gateway_id)

    def vpc_detach_internet_gateway(self, vpc_id, internet_gateway_id):
        return self.client().detach_internet_gateway(VpcId=vpc_id, InternetGatewayId=internet_gateway_id)

    def vpc_create(self, cidr_block='172.16.0.0/16', tags=None):
        kwargs = {  'CidrBlock'        : cidr_block                                                    ,
                    'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type='vpc')}
        return self.client().create_vpc(**kwargs).get('Vpc')           # todo: see if it makes sense to add the status_ok message here

    def vpc_delete(self, vpc_id):
        self.client().delete_vpc(VpcId=vpc_id)                          # add rest of normal delete methods

    def vpc_exists(self, vpc_id):
        return self.vpc(vpc_id) is not None

    def vpc_attribute_set(self, vpc_id, name, value):
        kvwags = {"VpcId" : vpc_id,
                  name :  {'Value' : value}}
        return self.client().modify_vpc_attribute(**kvwags)


    @index_by
    @group_by
    def vpcs(self, vpcs_ids=None):
        kwargs = {}
        if vpcs_ids:
            kwargs['VpcIds'] = vpcs_ids
        try:
            return self.client().describe_vpcs(**kwargs).get('Vpcs')
        except ClientError as e:                                            # todo: refactor this pattern into a helper with statement (which receives as param the Error.Code value
            if e.response.get('Error', {}).get('Code') == 'InvalidVpcID.NotFound':
                return []
            raise

    def vpcs_ids(self):
        return list_set(self.vpcs(index_by='VpcId'))

    def wait_for(self, waiter_type, kwargs):
        waiter = self.client().get_waiter(waiter_type)
        return waiter.wait(**kwargs)

    def wait_for_instance_status_ok(self, instance_id):
        return self.wait_for('instance_status_ok', {"InstanceIds": [instance_id]})

    def wait_for_instance_running(self, instance_id):
        return self.wait_for('instance_running', {"InstanceIds": [instance_id]})

    def wait_for_vpc_available(self, vpc_id):
        return self.wait_for('vpc_available', {"VpcIds": [vpc_id]})
