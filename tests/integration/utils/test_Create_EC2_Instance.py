from unittest import TestCase

from osbot_aws.aws.ec2.utils.Create_EC2_Instance import Create_EC2_Instance


class test_Create_EC2_Instance(TestCase):
    create_ec2_instance : Create_EC2_Instance

    @classmethod
    def setUpClass(cls):
        cls.create_ec2_instance = Create_EC2_Instance()

    def test__init__(self):
        expected_defaults = { 'image_id'         : ''    ,
                              'instance_type'    : ''    ,
                              'key_name'         : ''    ,
                              'target_region'    : ''    ,
                              'security_group_id': ''    ,
                              'spot_instance'    : True  ,
                              'tags'             : {}    }
        assert self.create_ec2_instance.__locals__() == expected_defaults

    def test_create_kwargs(self):
        with self.create_ec2_instance as _:
            assert _.create_kwargs() == _.__locals__()

    def test_set_image_id__aws_linux__for_region(self):
        with self.create_ec2_instance as _:
            #result = self.create_ec2_instance.set_image_id__aws_linux__for_region('eu-west-1')
            #pprint(result)
            pass
