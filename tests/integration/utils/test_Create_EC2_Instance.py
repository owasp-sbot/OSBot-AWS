import pytest

from osbot_aws.aws.ec2.EC2_Instance                 import EC2_Instance
from osbot_aws.aws.ec2.utils.EC2__Create__Instance  import EC2__Create__Instance
from osbot_aws.aws.ec2.utils.TestCase__EC2          import TestCase__EC2
from osbot_utils.utils.Env                          import not_in_github_action


class test_Create__EC2__Instance(TestCase__EC2):
    create_ec2_instance : EC2__Create__Instance

    def setUp(self):
        self.create_ec2_instance = EC2__Create__Instance(ec2=self.ec2)

    def expected__default_create_kwargs(self):
        return  { 'image_id'         : ''    ,
                  'instance_type'    : ''    ,
                  'key_name'         : ''    ,
                  'security_group_id': ''    ,
                  'spot_instance'    : True  ,
                  'tags'             : {}    }

    def test__init__(self):
        assert self.create_ec2_instance.__locals__() == { **self.expected__default_create_kwargs(),
                                                          'ec2' : self.ec2                       }

    def test_create_instance(self):
        if not_in_github_action():
            pytest.skip("no need to run this locally (only run this in GH Actions)")

        with self.create_ec2_instance as _:
            # create instance
            _.setup__with_amazon_linux__t3_name__ssh_sh__spot()
            instance_id      = _.create_instance()

            # check created instance details
            instance_details = _.ec2.instance_details(instance_id=instance_id)
            assert instance_details.get('instance_type') == 't3.nano'
            assert instance_details.get('architecture' ) == 'x86_64'
            assert instance_details.get('image_id'     ) == _.ami_amazon_linux_3_x86_64()
            assert instance_details.get('key_name'     ) == _.key_name__from_account_id_and_region_name()
            assert instance_details.get('spot_id'      ) is not None
            assert instance_details.get('spot_id'      ) is not None
            assert instance_details.get('tags'         ) == [{'Key': 'Name', 'Value': 'created by osbot_aws'},
                                                             {'Key': 'created-by', 'Value': 'OSBot_AWS.Create_EC2_Instance'}]
            # ssh into instance

            ec_instance     = EC2_Instance(instance_id=instance_id, ec2=_.ec2)
            ssh_key_file    = _.path_key_file()
            key_key_user    = 'ec2-user'
            ssh             = ec_instance.ssh(ssh_key_file, key_key_user)

            assert ec_instance.exists() is True
            ec_instance.wait_for_ssh()

            assert ssh.ssh_linux().pwd() == '/home/ec2-user'

            # delete instance
            ec_instance.delete()
            assert ec_instance.info().get('state') == {'Code': 32, 'Name': 'shutting-down'}


    def test_create_kwargs(self):
        with self.create_ec2_instance as _:
            assert _.create_kwargs() == self.expected__default_create_kwargs()


    # def test_security_group_with_ssh(self):
    #     with self.create_ec2_instance as _:
    #         security_group = _.security_group_with_ssh()

    def test_setup__with_amazon_linux__t3_name__ssh_sh__spot(self):
        with self.create_ec2_instance as _:
            _.setup__with_amazon_linux__t3_name__ssh_sh__spot()
            assert _.create_kwargs() == {'image_id'         : _.ami_amazon_linux_3_x86_64()       ,
                                         'instance_type'    : 't3.nano'                           ,
                                         'key_name'         : _.key_name__create_if_doesnt_exist(),
                                         'security_group_id': _.security_group_with_ssh()         ,
                                         'spot_instance'    : True                                ,
                                         'tags'             : {'created-by': 'OSBot_AWS.Create_EC2_Instance'}}

    # def test_key_name__create_if_doesnt_exist(self):
    #     with self.create_ec2_instance as _:
    #         _.key_name__create_if_doesnt_exist()
    #
    # def test_key_name__from_account_id_and_region_name(self):
    #     with self.create_ec2_instance as _:
    #         key_name = _.key_name__from_account_id_and_region_name()

    # def test_set_image_id__aws_linux__for_region(self):
    #     with self.create_ec2_instance as _:
    #         pprint(_.ec2.amis(owner='amazon', architecture='x86_64', description='Amazon Linux AMI'))


    # def test_path_key_file(self):
    #     with self.create_ec2_instance as _:
    #         path_key_file = _.path_key_file()