from os import chmod

import boto3
from botocore.exceptions import ClientError

from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Lists import list_index_by, list_get

from osbot_aws.AWS_Config import set_aws_region, AWS_Config
from osbot_utils.decorators.methods.cache_on_self import cache_on_self
from osbot_utils.utils.Files import file_name, temp_folder, path_combine, file_create

from osbot_utils.decorators.methods.remove_return_value import remove_return_value

from osbot_utils.decorators.lists.group_by import group_by
from osbot_utils.decorators.lists.index_by import index_by
from osbot_utils.decorators.methods.cache import cache
from osbot_aws.apis.Session import Session
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Status import status_warning, status_ok

# todo: find good solution to capture/manage these config values
EC2_WAITER_DELAY        = 1             # default was 15 seconds
EC2_WAITER_MAX_ATTEMPTS = 600           # default was 40 times

class EC2(Type_Safe):

    aws_config : AWS_Config

    @cache_on_self
    def client(self):
        return Session().client('ec2')

    @cache_on_self
    def resource(self):                     # todo: refactor this out and only use client() for all calls
        return Session().resource('ec2')

    def ami(self, ami_id):
        #result = self.amis(ami_id=ami_id)
        images = self.client().describe_images(ImageIds=[ami_id]).get('Images')
        if len(images) == 1:
            return images.pop()

    @index_by
    @group_by
    def amis(self, owner='self', architecture=None, state='available', name=None, description=None, ami_id=None, **kwargs):  # todo: find how to search for amis in the quick start
        filters = [{'Name': 'state', 'Values': [state]}]
        if architecture : filters.append({'Name': 'architecture', 'Values': [architecture]})
        if name         : filters.append({'Name': 'name'        , 'Values': [name        ]})
        if description  : filters.append({'Name': 'description' , 'Values': [description ]})
        if ami_id       : filters.append({'Name': 'image-id'    , 'Values': [ami_id      ]})
        for key,value in kwargs.items():
            filters.append({'Name': key, 'Values': [value]})
        describe_kwargs = {'Owners': [owner],
                           'Filters':filters }
        pprint(describe_kwargs)
        return self.client().describe_images(**describe_kwargs).get('Images')

    def image(self, image_id):
        return self.ami(ami_id=image_id)

    def instance_create(self, image_id                                      ,   # only var needed is the image_id which is region specific
                              dry_run               = False                 ,   # todo: refactor into a EC2_Create_Instance helper class
                              block_device_mappings = None                  ,
                              instance_type         = 't2.micro'            ,
                              iam_instance_profile  = None                  ,
                              spot_instance         = False                 ,
                              key_name              = None                  ,
                              name                  = 'created by osbot_aws',
                              network_interface     = None                  ,
                              tags                  = None                  ,
                              security_group_id     = None                  ):


        kwargs = {  "ImageId"      : image_id                                                               ,
                    "InstanceType" : instance_type                                                          ,
                    "MaxCount"     : 1                                                                      ,
                    "MinCount"     : 1                                                                      ,
                    'TagSpecifications': self.tag_specifications_create(tags=tags, name=name,resource_type='instance')}

        if block_device_mappings : kwargs["BlockDeviceMappings"] = block_device_mappings
        if iam_instance_profile  : kwargs["IamInstanceProfile" ] = iam_instance_profile
        if key_name              : kwargs["KeyName"            ] = key_name
        if network_interface     : kwargs['NetworkInterfaces'  ] = [network_interface]
        if security_group_id     : kwargs['SecurityGroupIds'   ] = [security_group_id]
        if spot_instance:
            max_spot_price                  = '0.1'                     # max price to pay
            spot_instance_type              = 'one-time'                # or 'persistent'
            interrupt_behaviour             = 'terminate'               # or 'stop' or 'hibernate'
            kwargs['InstanceMarketOptions'] = { 'MarketType' : 'spot',
                                                'SpotOptions': { 'MaxPrice'                    : max_spot_price      ,
                                                                 'SpotInstanceType'            : spot_instance_type  ,
                                                                 'InstanceInterruptionBehavior': interrupt_behaviour }}
        if dry_run:
            return kwargs

        result   = self.client().run_instances(**kwargs)
        instance = result.get('Instances')[0]
        return  instance.get('InstanceId')

    def create_image(self, instance_id, name, description=None, no_reboot=False, tags=None):
        kwargs = { 'InstanceId' : instance_id ,
                   'Name'       : name        }
        if description: kwargs['Description'] = description
        if no_reboot  : kwargs['NoReboot'   ] = no_reboot
        if tags       : kwargs['TagSpecifications'] = self.tag_specifications_create(tags=tags, resource_type='image')
        return self.client().create_image(**kwargs).get('ImageId')
    def format_instance_details(self, target):
        if target:
            instance_details = { 'architecture'     : target.architecture                         ,
                                 'availability_zone': target.placement.get('AvailabilityZone')    ,
                                 'block_devices'    : {}                                          ,
                                 'cpus'             : target.cpu_options['CoreCount']             ,
                                 'image_id'         : target.image_id                             ,
                                 'instance_type'    : target.instance_type                        ,
                                 'instance_id'      : target.instance_id                          ,
                                 'key_name'         : target.key_name                             ,
                                 'launch_time'      : target.meta.data.get('LauchTime')           ,
                                 'private_ip'       : target.private_ip_address                   ,
                                 'public_ip'        : target.public_ip_address                    ,
                                 'subnet_id'        : target.meta.data.get('SubnetId')            ,
                                 'spot_id'          : target.spot_instance_request_id             ,
                                 'state'            : target.state                                ,
                                 'tags'             : target.tags                                 ,
                                 'vpc_id'           : target.meta.data.get('VpcId')               }

            for block_device_mapping in target.block_device_mappings:
                block_device_name = block_device_mapping.get('DeviceName')
                ebs_data = block_device_mapping.get('Ebs')
                if ebs_data is None:
                    block_device = {"block_type": 'unknown' }               # todo: handle better (including with logging) this scenario (see if there are other possible values for this)
                else:
                    block_device      = {"block_type" : "Ebs"                          ,
                                         "status"     : str(ebs_data.get('Status'    )),
                                         "volume_id"  : str(ebs_data.get('VolumeId'  ))}
                instance_details.get('block_devices')[block_device_name] = block_device

            return instance_details

    def instance_block_devices(self, instance_id):
        instance = self.instance_details_raw(instance_id)
        if instance:
            return list_index_by(instance.block_device_mappings, "DeviceName")

    def instance_details(self, instance_id):
        instance = self.instance_details_raw(instance_id)
        return self.format_instance_details(instance)

    def instance_details_raw(self, instance_id):
        kwargs = { }
        if instance_id: kwargs['InstanceIds'] = [instance_id]
        result = self.resource().instances.filter(**kwargs)             # todo see client().describe_instances is a better method to use
        for instance in result:
            return instance

    def instance_delete(self, instance_id):
        if self.instance_exists(instance_id):
            result = self.client().terminate_instances(InstanceIds=[instance_id])
            return list_get(result.get('TerminatingInstances'),0)

    def instance_exists(self, instance_id):
        return self.instance_details(instance_id=instance_id) is not None

    def instances_details(self, filters=None):
        instances = {}
        if filters is None:
            resource_data = self.resource().instances.all()
        else:
            if type(filters) is not list:
                filters=[filters]
            resource_data = self.resource().instances.filter(Filters=filters)
        for instance in resource_data:
            instance_id = instance.instance_id
            instances[instance_id] = self.format_instance_details(instance)
        return instances

    def instance_start(self, instance_id):
        self.client().start_instances(InstanceIds=[instance_id])

    def instance_stop(self, instance_id):
        self.client().stop_instances(InstanceIds=[instance_id])

    def instance_terminate(self, instance_id):
        self.client().terminate_instances(InstanceIds=[instance_id])

    def instance_volumes_ids(self, instance_id):
        volume_ids = []
        for block_device in self.instance_block_devices(instance_id).values():
            volume_id = block_device.get('Ebs', {}).get('VolumeId')                 # todo: see what other options could exist apart from EBS
            if volume_id:
                volume_ids.append(volume_id)
        return volume_ids

    @index_by
    @group_by
    def instance_volumes(self, instance_id=None):
        volumes_ids = []
        if instance_id:
            volumes_ids = self.instance_volumes_ids(instance_id)
        return self.volumes(volumes_ids)

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

    def security_group_default(self):
        default_vpc_id  = self.vpc_default().get('VpcId')
        default_groups  =  self.security_groups(group_by='GroupName').get('default')
        for default_group in default_groups:
            if default_group.get('VpcId') == default_vpc_id:
                return default_group

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

    @index_by
    def subnet_default_for_az(self, az_index=1):
        return list_get(self.subnets_default_for_az(), az_index)

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

    @index_by
    def subnets_default_for_az(self):
        return self.subnets(group_by='DefaultForAz').get(True)

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

    def volume(self, volume_id=None):
        if volume_id:
            volumes = self.volumes([volume_id])
            if len(volumes) ==1:
                return volumes.pop()

    def volumes(self, volumes_ids=None):
        if volumes_ids:
            return self.client().describe_volumes(VolumeIds=volumes_ids).get('Volumes')
        return []

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

    def vpc_default(self):
        return self.vpcs(index_by='IsDefault').get(True)

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
        waiter.config.delay        = EC2_WAITER_DELAY
        waiter.config.max_attempts = EC2_WAITER_MAX_ATTEMPTS
        return waiter.wait(**kwargs)

    def wait_for_instance_exists    (self, instance_id): return self.wait_for('instance_exists'     , {"InstanceIds": [instance_id]})
    def wait_for_instance_status_ok (self, instance_id): return self.wait_for('instance_status_ok'  , {"InstanceIds": [instance_id]})
    def wait_for_instance_running   (self, instance_id): return self.wait_for('instance_running'    , {"InstanceIds": [instance_id]})
    def wait_for_instance_stopped   (self, instance_id): return self.wait_for('instance_stopped'    , {"InstanceIds": [instance_id]})
    def wait_for_instance_terminated(self, instance_id): return self.wait_for('instance_terminated' , {"InstanceIds": [instance_id]})

    def wait_for_vpc_available      (self, vpc_id     ): return self.wait_for('vpc_available', {"VpcIds": [vpc_id]})


def get_EC2_in_region(region_name):                     # this method is not thread save
    set_aws_region(region_name=region_name)         # because this is a global value
    ec2 = EC2()
    ec2.client()                                    # get these value cached (since they depend on the global config value)
    ec2.resource()                                  # get these value cached (since they depend on the global config value)
    return ec2