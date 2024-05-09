from osbot_aws.apis.EC2 import EC2
from osbot_utils.utils.Misc import random_string

from osbot_aws.helpers.AMI import AMI


class EC2_Instance:
    def __init__(self, instance_id=None, create_kwargs=None):
        self.create_kwargs = create_kwargs
        self.instance_id   = instance_id
        self.ec2           = EC2()

    def create(self):
        kwargs = self.create_kwargs
        random_name = random_string(prefix='test_ec2_with_ssh_support')
        if not kwargs.get('image_id'     ): kwargs['image_id'     ] = AMI().amazon_linux_2()
        if not kwargs.get('instance_type'): kwargs['instance_type'] = 't2.nano'
        if not kwargs.get('name'         ): kwargs['name'         ] = random_name
        if not kwargs.get('tags'         ): kwargs['tags'         ] = {'Type': 'EC2_Instance'}

        self.instance_id = self.ec2.instance_create(**kwargs)
        return self.instance_id

    def delete(self):
        return self.ec2.instance_delete(instance_id=self.instance_id)

    def exists(self):
        return self.ec2.instance_exists(instance_id=self.instance_id)

    def info(self):
        return self.ec2.instance_details(instance_id=self.instance_id)

    def state(self):
        return self.info().get('state')

    def tags(self):
        return self.info().get('tags')