import boto3
from osbot_utils.decorators.methods.cache import cache

from osbot_aws.apis.Session import Session


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

        kwargs["TagSpecifications"] = [{"ResourceType": "instance"      ,
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

    def security_groups(self):
        groups={}
        for group in self.client().describe_security_groups().get('SecurityGroups'):
            groups[group.get('GroupId')] = group
        return groups

    def subnets(self):
        subnets = {}
        for subnet in self.client().describe_subnets().get('Subnets'):
            subnets[subnet.get('SubnetId')] = subnet
        return subnets

    def vpcs(self):
        vpcs = {}
        for vpc in self.client().describe_vpcs().get('Vpcs'):
            vpcs[vpc.get('VpcId')] = vpc
        return vpcs

    def wait_for(self, waiter_type, instance_id):
        waiter = self.client().get_waiter(waiter_type)
        return waiter.wait(InstanceIds=[instance_id])

    def wait_for_instance_status_ok(self, instance_id):
        self.wait_for('instance_status_ok', instance_id)

    def wait_for_instance_running(self, instance_id):
        self.wait_for('instance_running', instance_id)
