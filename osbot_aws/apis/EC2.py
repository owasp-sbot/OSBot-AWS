import boto3
from botocore.exceptions import ClientError
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

    def instance_create(self, image_id, name='created by osbot_aws', instance_type='t2.micro', tags=None, iam_instance_profile=None):
        kwargs = {
            "ImageId"      : image_id       ,
            "InstanceType" : instance_type  ,
            "MaxCount"     : 1              ,
            "MinCount"     : 1
        }

        if iam_instance_profile:
            kwargs["IamInstanceProfile"] = iam_instance_profile

        instance_tags = [{'Key': 'Name', 'Value': name}]
        if tags and type(tags) is dict:
            for key,value in tags.items():
                instance_tags.append({'Key': key, 'Value': value})

        kwargs["TagSpecifications"] = [{"ResourceType": "instance"      ,       # todo: refactor this code with a call to self.tag_specifications_create()
                                        "Tags"        : instance_tags }]


        result = self.client().run_instances(**kwargs)
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
        result = self.resource().instances.filter(**kwargs)
        for instance in result:
            return self.format_instance_details(instance)       # todo see client().describe_instances is a better method to use
        #result = self.client().describe_instances(InstanceIds=[instance_id])
        #return result.get('Reservations')[0].get('Instances')[0]

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

    def internet_gateway_create(self, tags=None, resource_type='internet-gateway'):
        kwargs = { 'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type=resource_type) }
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

    def security_group(self, group_id=None, group_name=None):
        if group_id:
            return self.security_groups(index_by="GroupId"  ).get(group_id)
        if group_name:
            return self.security_groups(index_by="GroupName").get(group_name)

    #authorize_security_group_ingress
    def security_group_create(self, group_name, description, vpc_id=None, resource_type=None, tags=None):
        if self.security_group_exists(group_name=group_name):
            group_id =  self.security_group(group_name=group_name).get('GroupId')            # todo see what is a better way to implement this workflow, since at the moment there are two full calls to the self.security_groups() method
            return status_warning(message=f'Security group already existed: {group_name}' , data= { 'group_id':group_id })
        kwargs = { 'Description'       : description,
                   'GroupName'         : group_name ,
                   'TagSpecifications' : []         }
        if vpc_id:
            kwargs['VpcId'] = vpc_id
        if tags:
            tag_specification = {'Tags': []}    # todo: refactor this code with a call to self.tag_specifications_create()
            for key,value in tags.items():
                tag_specification['Tags'].append({'Key':key, 'Value':value})
            kwargs['TagSpecifications'].append(tag_specification)


        group_id = self.client().create_security_group(**kwargs).get('GroupId')
        return status_ok(message=f'Security group created ok: {group_name}', data= { 'group_id':group_id })
        #
        # Description = 'string',
        # GroupName = 'string',
        # VpcId = '

        # Tags

    def security_group_delete(self, group_id=None, group_name=None):
        if group_id:
            self.client().delete_security_group(GroupId=group_id)
        if group_name:
            self.client().delete_security_group(GroupName=group_name)
        return self.security_group_exists(group_id=group_id, group_name=group_name) is False

    def security_group_exists(self, group_id=None, group_name=None):
        return self.security_group(group_id=group_id, group_name=group_name) is not None

    @index_by
    @group_by
    def security_groups(self):
        return self.client().describe_security_groups().get('SecurityGroups')

    @index_by
    @group_by
    def subnets(self):
        return self.client().describe_subnets().get('Subnets')

    def tag_specifications_create(self, tags=None, resource_type=None):
        data =  []
        if tags:
            tag_specification = { 'Tags': []}
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

    def vpc_create(self, cidr_block='172.16.0.0/16', tags=None, resource_type='vpc'):
        kwargs = {
            'CidrBlock'        : cidr_block                                          ,
            'TagSpecifications': self.tag_specifications_create(tags=tags, resource_type=resource_type)
        }
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
