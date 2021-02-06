from osbot_aws.apis.EC2 import EC2
from osbot_utils.utils.Misc import random_string

from osbot_aws.helpers.AMI import AMI


class EC2_Instance:
    def __init__(self, instance_id=None, image_id=None, name=None, tags=None):
        self.image_id    = image_id or AMI().amazon_linux_2()
        self.name        = name     or random_string(prefix='test_ec2_with_ssh_support-')
        self.tags        = tags     or {'Name': f'osbot_aws - {name}'}
        self.instance_id = instance_id
        self.ec2         = EC2()

    def create(self):
        kwargs   = { "image_id" : self.image_id ,
                     "name"     : self.name     ,
                     "tags"     : self.tags     }
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