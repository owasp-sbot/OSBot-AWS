from os import environ

from osbot_aws.aws.ec2.AMI import AMI
from osbot_aws.aws.ec2.EC2                      import EC2
from osbot_utils.base_classes.Kwargs_To_Self    import Kwargs_To_Self
from osbot_utils.helpers.ssh.SSH                import SSH
from osbot_utils.helpers.ssh.SSH__Execute       import ENV_VAR__SSH__HOST, ENV_VAR__SSH__KEY_FILE, ENV_VAR__SSH__USER
from osbot_utils.utils.Dev                      import pprint
from osbot_utils.utils.Http                     import wait_for_ssh
from osbot_utils.utils.Misc                     import random_string

class EC2_Instance(Kwargs_To_Self):
    instance_id   : str
    create_kwargs : dict
    ec2           : EC2
    # def __init__(self, instance_id=None, create_kwargs=None):
    #     self.create_kwargs = create_kwargs
    #     self.instance_id   = instance_id
    #     self.ec2           = EC2()

    def create(self, instance_name = None):
        kwargs = self.create_kwargs
        random_name = random_string(prefix='test_ec2_with_ssh_support')
        if not kwargs.get('image_id'     ): kwargs['image_id'     ] = AMI().amazon_linux_3()
        if not kwargs.get('instance_type'): kwargs['instance_type'] = 't2.nano'
        if not kwargs.get('name'         ): kwargs['name'         ] = instance_name or random_name
        if not kwargs.get('tags'         ): kwargs['tags'         ] = {'Type': 'EC2_Instance'}

        self.instance_id = self.ec2.instance_create(**kwargs)
        return self.instance_id

    def delete(self):
        return self.ec2.instance_delete(instance_id=self.instance_id)

    def exists(self):
        return self.ec2.instance_exists(instance_id=self.instance_id)

    def info(self):
        return self.ec2.instance_details(instance_id=self.instance_id)

    def print_info(self):
        pprint(self.info())

    def ip_address(self):
        return self.info().get('public_ip')

    def start(self):
        return self.ec2.instance_start(instance_id=self.instance_id)

    def stop(self):
        return self.ec2.instance_terminate(instance_id=self.instance_id)

    def ssh(self, ssh_key_file, ssh_key_user):
        ip_address = self.ip_address()
        ssh = SSH()
        environ[ENV_VAR__SSH__HOST    ] = ip_address
        environ[ENV_VAR__SSH__KEY_FILE] = ssh_key_file          # todo: redo this workflow on how to set up the ssh_execute obejct
        environ[ENV_VAR__SSH__USER    ] = ssh_key_user
        ssh.ssh_execute().setup()
        return ssh

    def state(self):
        return self.info().get('state')

    def tags(self):
        return self.info().get('tags')

    def wait_for_ssh(self):
        return wait_for_ssh(self.ip_address())