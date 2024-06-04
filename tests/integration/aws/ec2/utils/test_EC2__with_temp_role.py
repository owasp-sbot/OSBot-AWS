from unittest import TestCase

from osbot_aws.OSBot_Setup import CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID, \
    CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION, CURRENT__OSBOT_AWS__TESTS__IAM_USER
from osbot_aws.aws.ec2.utils.EC2__with_temp_role import EC2__with_temp_role
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Objects import obj_info

class test_EC2__with_temp_role(TestCase):

    def setUp(self):
        self.ec2__with_temp_role = EC2__with_temp_role()

    # todo: wire this when OSBOT in GH is running with the new AWS account
    # def test___check_current_identity(self):
    #     with self.ec2__with_temp_role.aws_config as _:
    #         assert _.account_id()                == CURRENT__OSBOT_AWS__TESTS__ACCOUNT_ID
    #         assert _.aws_session_region_name()   == CURRENT__OSBOT_AWS__TESTS__DEFAULT_REGION
    #         assert _.sts__caller_identity_user() == CURRENT__OSBOT_AWS__TESTS__IAM_USER

    def test___init__(self):
        with self.ec2__with_temp_role  as _:
            expected_values = { '_temp_role_config' : _._temp_role_config  ,
                                'aws_config'         : _.aws_config         }
            assert _.__locals__() == expected_values

    # def test__iam_assume_role(self):
    #     with self.ec2__with_temp_role as _:
    #
    #         iam_assume_policy = _._iam_assume_role()

    # def test_client(self):
    #     obj_info(self.ec2__with_temp_role)
    #
    #     #pprint(self.ec2__with_temp_role.)
    #     #pprint(self.ec2__with_temp_role.amis())