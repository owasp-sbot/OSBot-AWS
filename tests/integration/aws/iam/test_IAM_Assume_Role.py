from unittest import TestCase

import boto3
import pytest

from osbot_aws.apis.Cloud_Trail import Cloud_Trail
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import folder_exists, parent_folder, current_temp_folder, folder_name
from osbot_utils.utils.Misc import list_set
from osbot_utils.utils.Objects import obj_info
from osbot_utils.utils.Status import osbot_logger

from osbot_aws.aws.iam.IAM_Assume_Role import IAM_Assume_Role

TEMP_ROLE_NAME__ASSUME_ROLE = 'osbot_aws_temp_role__assume_role'
TEST_POLICY_DOCUMENT        = { "Version": "2012-10-17",
                                "Statement": [ { "Effect"  : "Allow"               ,
                                                 "Action"  : "s3:ListAllMyBuckets" ,
                                                 "Resource": "*"                  }]}
class test_IAM_Assume_Role(TestCase):

    def setUp(self):
        self.iam_assume_role = IAM_Assume_Role(role_name=TEMP_ROLE_NAME__ASSUME_ROLE)

    def test__init__(self):
        assert self.iam_assume_role.role_name        == TEMP_ROLE_NAME__ASSUME_ROLE

    def test_create_policy_document(self):
        expect_policy_document = { "Version": "2012-10-17",
                                   "Statement": [ { "Effect"  : "Allow"                   ,
                                                    "Action"  : "cloudtrail:LookupEvents" ,
                                                    "Resource": "*"                       }]}
        effect   = "Allow"
        service  = "cloudtrail"
        action   = "LookupEvents"
        resource = "*"
        kwargs = dict(effect=effect, service=service, action=action, resource=resource)
        assert self.iam_assume_role.create_policy_document(**kwargs) == expect_policy_document


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

        assert list_set(self.iam_assume_role.data()) == ['assume_policy','current_account_id','current_user_arn','current_user_id','policies', 'result__credentials', 'result__role_create','role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.role_exists() is True


    def test_credentials(self):
        credentials = self.iam_assume_role.credentials()
        assert list_set(credentials) == ['AccessKeyId', 'SecretAccessKey', 'SessionToken']

    def test_credentials_raw(self):
        credentials = self.iam_assume_role.credentials_raw()
        assert list_set(credentials) == ['AssumedRoleUser', 'Credentials']
        assert list_set(credentials['AssumedRoleUser']) == ['Arn', 'AssumedRoleId']
        assert list_set(credentials['Credentials'    ]) == ['AccessKeyId', 'Expiration', 'SecretAccessKey', 'SessionToken']

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

    def test_policies(self):
        policies = self.iam_assume_role.policies()
        assert type(policies) == dict

    #@print_boto3_calls()
    def test_set_inline_policy(self):
        policy_name     = 'test_policy'
        policy_document = TEST_POLICY_DOCUMENT
        self.iam_assume_role.set_inline_policy(policy_name, policy_document)

        assert TEST_POLICY_DOCUMENT == {"Version": "2012-10-17",
                                        "Statement": [ { "Effect"   : "Allow"              ,
                                                         "Action"  : "s3:ListAllMyBuckets" ,
                                                         "Resource": "*"                   }]}

        policies = self.iam_assume_role.policies()
        assert policies[policy_name] == policy_document

        s3_client             = self.iam_assume_role.boto3_client('s3')
        sts_client            = self.iam_assume_role.boto3_client('sts')
        user_identity         = sts_client.get_caller_identity()
        role_data             = self.iam_assume_role.data()
        current_account_id    = role_data.get('current_account_id')
        result__credentials   = role_data.get('result__credentials')
        assumed_role_user_arn = result__credentials.get('AssumedRoleUser').get('Arn')
        assumed_role_user_id  = result__credentials.get('AssumedRoleUser').get('AssumedRoleId')

        assert s3_client.meta.service_model.service_name  == 's3'
        assert sts_client.meta.service_model.service_name == 'sts'
        assert user_identity['Account']                   == current_account_id
        assert user_identity['Arn'    ]                   == assumed_role_user_arn
        assert user_identity['UserId' ]                   == assumed_role_user_id

        assert len(s3_client.list_buckets()) > 0

    def test_role_arn(self):
        data     = self.iam_assume_role.data()
        role_arn = self.iam_assume_role.role_arn()
        assert role_arn == f"arn:aws:iam::{data.get('current_account_id')}:role/{self.iam_assume_role.role_name}"

    #@print_boto3_calls()
    def test_setup_data(self):
        self.iam_assume_role.reset()                                # deletes the cache
        setup_data = self.iam_assume_role.setup_data()
        assert list_set(setup_data) == [ 'assume_policy', 'current_account_id', 'current_user_arn','current_user_id','policies',
                                         'result__credentials' , 'result__role_create',
                                         'role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.cached_role.cache_exists() is True


class test_Cloud_Trail_Lookup(TestCase):

    #@print_boto3_calls(config__print_return_value=True)
    def test_get_cloud_trail_logs(self):
        role_name            = "temp_role__for_cloud_trail_logs"

        self.iam_assume_role = IAM_Assume_Role(role_name=role_name)
        self.iam_assume_role.create_role(recreate=False)

        client          = self.iam_assume_role.boto3_client(service_name='cloudtrail')
        policy_name     = 'cloud_trail_logs_policy'
        policy_document = self.iam_assume_role.create_policy_document( service='cloudtrail', action='LookupEvents', resource='*')

        self.iam_assume_role.set_inline_policy(policy_name, policy_document)
        self.iam_assume_role.add_policy(service='cloudtrail', action='LookupEvents', resource='*')

        cloud_trail            = Cloud_Trail()
        cloud_trail.cloudtrail = client
        events = cloud_trail.events_in_last(50, page_size=1)
        assert list_set(next(events)) == ['AccessKeyId', 'CloudTrailEvent', 'EventId', 'EventName', 'EventSource', 'EventTime', 'ReadOnly', 'Resources', 'Username']



# todo create another example for dynamodb:ListTables

# policy_statements = [{
#         "Effect": "Allow",
#         "Action": "dynamodb:ListTables",
#         "Resource": "arn:aws:dynamodb:eu-west-2:{account_id}:table/*"}]
# policy_document = { "Version": "2012-10-17",
#                     "Statement": policy_statements}
