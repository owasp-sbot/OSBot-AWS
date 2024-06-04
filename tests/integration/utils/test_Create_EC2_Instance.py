from osbot_aws.aws.ec2.utils.EC2__Create__Instance import EC2__Create__Instance
from osbot_aws.aws.ec2.utils.TestCase__EC2         import TestCase__EC2


class test_Create__EC2__Instance(TestCase__EC2):
    create_ec2_instance : EC2__Create__Instance

    def setUp(self):
        self.create_ec2_instance = EC2__Create__Instance(ec2=self.ec2)

    def expected__default_create_kwargs(self):
        return  { 'image_id'         : ''    ,
                  'instance_type'    : ''    ,
                  'key_name'         : ''    ,
                  'target_region'    : ''    ,
                  'security_group_id': ''    ,
                  'spot_instance'    : True  ,
                  'tags'             : {}    }

    def test__init__(self):
        assert self.create_ec2_instance.__locals__() == { **self.expected__default_create_kwargs(),
                                                          'ec2' : self.ec2                       }

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
                                         'tags'             : {'created-by': 'OSBot_AWS.Create_EC2_Instance'},
                                         'target_region'    : self.ec2.aws_config.region_name()   }

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