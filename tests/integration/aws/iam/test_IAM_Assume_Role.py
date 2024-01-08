from unittest import TestCase

import pytest

from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, parent_folder, current_temp_folder, folder_name
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Status import osbot_logger

from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role

TEMP_ROLE_NAME__ASSUME_ROLE = 'osbot_aws_temp_role__assume_role'
TEST_POLICY_DOCUMENT = {"Version": "2012-10-17",
                         "Statement": [ { "Effect"   : "Allow"        ,
                                          "Action"  : "s3:ListBucket" ,
                                          "Resource": "*"             }]}
class test_IAM_Assume_Role(TestCase):

    def setUp(self):
        self.iam_assume_role = IAM_Assume_Role(role_name=TEMP_ROLE_NAME__ASSUME_ROLE)

    def test__init__(self):
        assert self.iam_assume_role.role_name        == TEMP_ROLE_NAME__ASSUME_ROLE
        #assert self.iam_assume_role.policy_statement == TEST_POLICY_DOCUMENT
        #assert self.iam_assume_role.cached_role.cache_exists() is False


    @pytest.mark.skip('fix test, current throwing error: error creating role with assume_policy_document')
    def test_create_role(self):
        print()
        osbot_logger.add_console_logger()
        result = self.iam_assume_role.create_role()

        pprint(osbot_logger.memory_handler_messages())
        #assert result.get('role_exists'). is False
        #pprint(result)#


    def test_role_exists(self):
        assert self.iam_assume_role.role_exists() is False

    # def test_path_cached_roles(self):
    #     path_folder = self.iam_assume_role.path_cached_roles()
    #     assert folder_exists(path_folder) is True
    #     assert parent_folder(path_folder) == current_temp_folder()
    #     assert folder_name  (path_folder) == FOLDER_NAME__CACHED_ROLES

    def test_setup_data(self):
        #self.iam_assume_role.cached_role.cache_delete()
        setup_data = self.iam_assume_role.setup_data()
        assert list_set(setup_data) == [ 'assume_policy', 'current_account_id', 'current_user_arn',
                                         'current_user_id', 'role_exists', 'role_name']
        assert self.iam_assume_role.cached_role.cache_exists() is True
        #assert self.iam_assume_role.create_role().get('role_exists') is False
        #pprint(self.iam_assume_role.create_role())
