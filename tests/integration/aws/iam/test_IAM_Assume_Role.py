from unittest import TestCase

import pytest

from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, parent_folder, current_temp_folder, folder_name
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import obj_info
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


    #@pytest.mark.skip('fix test, current throwing error: error creating role with assume_policy_document')
    #@print_boto3_calls()
    def test_create_role(self):
        print()
        self.iam_assume_role.reset()                                        # reset cache (delete and create a new one)
        assert self.iam_assume_role.cached_role.cache_exists() is True      # check that cache doesn't exist

        self.iam_assume_role.delete_role()                                  # delete role
        assert self.iam_assume_role.role_exists()              is False     # check that cache doesn't exist

        self.iam_assume_role.create_role()                                  # create role

        assert self.iam_assume_role.cached_role.cache_exists() is True     # check that cache doesn't exist
        assert self.iam_assume_role.role_exists()              is True     # check that cache doesn't exist

        assert list_set(self.iam_assume_role.data()) == ['assume_policy','current_account_id','current_user_arn','current_user_id','result__role_create','role_exists','role_name']
        assert self.iam_assume_role.role_exists() is True

    def test_data(self):
        self.iam_assume_role.reset()
        assert self.iam_assume_role.data().get('role_name') == TEMP_ROLE_NAME__ASSUME_ROLE


    def test_default_assume_policy(self):
        assert self.iam_assume_role.default_assume_policy(                      ) == {'Version': '2012-10-17','Statement': []}
        assert self.iam_assume_role.default_assume_policy(user_arn='an_user_arn') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'AWS': 'an_user_arn'}}]}
        assert self.iam_assume_role.default_assume_policy(service_name='service') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'Service': 'service'}}]}
        assert self.iam_assume_role.default_assume_policy(federated='federated' ) == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'Federated': 'federated'}}]}
        assert self.iam_assume_role.default_assume_policy(canonical_user='user' ) == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                                             'Effect': 'Allow',
                                                                                                                             'Principal': {'CanonicalUser': 'user'}}]}
        assert self.iam_assume_role.default_assume_policy(user_arn='an_user_arn',
                                                          service_name='service',
                                                          federated='federated',
                                                          canonical_user='user') == {'Version': '2012-10-17','Statement': [{'Action': 'sts:AssumeRole',
                                                                                                    'Effect': 'Allow',
                                                                                                    'Principal': {'AWS': 'an_user_arn'}},
                                                                                                   {'Action': 'sts:AssumeRole',
                                                                                                    'Effect': 'Allow',
                                                                                                    'Principal': {'Service': 'service'}},
                                                                                                   {'Action': 'sts:AssumeRole',
                                                                                                    'Effect': 'Allow',
                                                                                                    'Principal': {'Federated': 'federated'}},
                                                                                                   {'Action': 'sts:AssumeRole',
                                                                                                    'Effect': 'Allow',
                                                                                                    'Principal': {'CanonicalUser': 'user'}}]}

    # def test_path_cached_roles(self):
    #     path_folder = self.iam_assume_role.path_cached_roles()
    #     assert folder_exists(path_folder) is True
    #     assert parent_folder(path_folder) == current_temp_folder()
    #     assert folder_name  (path_folder) == FOLDER_NAME__CACHED_ROLES

    #@print_boto3_calls()
    def test_setup_data(self):
        #self.iam_assume_role.cached_role.cache_delete()
        setup_data = self.iam_assume_role.setup_data()
        assert list_set(setup_data) == [ 'assume_policy', 'current_account_id', 'current_user_arn',
                                         'current_user_id', 'role_exists', 'role_name']
        assert self.iam_assume_role.cached_role.cache_exists() is True

        #pprint(self.iam_assume_role.cached_role.data())
        #assert self.iam_assume_role.create_role().get('role_exists') is False
        #pprint(self.iam_assume_role.create_role())
