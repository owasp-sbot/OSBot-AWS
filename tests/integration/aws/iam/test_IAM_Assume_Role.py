from unittest                           import TestCase

import pytest

from osbot_aws.testing.Pytest                   import skip_pytest___aws_pytest_user_name__is_not_set
from osbot_aws.testing.TestCase__Boto3_Cache    import TestCase__Boto3_Cache
from osbot_utils.utils.Misc                     import list_set
from osbot_aws.aws.iam.IAM_Assume_Role          import IAM_Assume_Role

TEMP_ROLE_NAME__ASSUME_ROLE = 'osbot_aws_temp_role__assume_role'
TEST_POLICY_DOCUMENT        = { "Version": "2012-10-17",
                                "Statement": [ { "Effect"  : "Allow"               ,
                                                 "Action"  : "s3:ListAllMyBuckets" ,
                                                 "Resource": "*"                  }]}

# note: none of these tests support caching
@pytest.mark.skip("Needs debug on reasons why it hangs 50% of the time ")
class test_IAM_Assume_Role(TestCase__Boto3_Cache):
    iam_assume_role : IAM_Assume_Role

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        skip_pytest___aws_pytest_user_name__is_not_set()
        cls.iam_assume_role = IAM_Assume_Role(role_name=TEMP_ROLE_NAME__ASSUME_ROLE)

    #@print_boto3_calls()
    def test_create_role(self):
        self.iam_assume_role.reset()                                        # reset cache (delete and create a new one)
        assert self.iam_assume_role.cached_role.cache_exists() is True      # check that cache doesn't exist

        self.iam_assume_role.delete_role()                                  # delete role
        assert self.iam_assume_role.role_exists()              is False     # check that cache doesn't exist

        self.iam_assume_role.create_role()                                  # create role

        assert self.iam_assume_role.cached_role.cache_exists() is True     # check that cache doesn't exist
        assert self.iam_assume_role.role_exists()              is True     # check that cache doesn't exist

        assert list_set(self.iam_assume_role.data()) == ['assume_policy','current_account_id','current_user_arn','current_user_id','policies', 'policies_to_add', 'result__credentials', 'result__role_create','role_arn','role_exists', 'role_name']
        assert self.iam_assume_role.role_exists() is True

    def test_credentials(self):
        credentials = self.iam_assume_role.credentials()
        assert list_set(credentials) == ['AccessKeyId', 'SecretAccessKey', 'SessionToken']

    def test_policies(self):
        policies = self.iam_assume_role.policies()
        assert type(policies) == dict

    #@print_boto3_calls()
    # note: this can take quite a while, sometimes 7 or 10 seconds
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

        result = self.iam_assume_role.wait_for_valid_execution('s3', 'list_buckets')
        assert type(result) is dict
        #assert len(result.get('Buckets')) > 0



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
        #assert user_identity['Arn'    ]                   == assumed_role_user_arn         # todo: add support for running in cache
        #assert user_identity['UserId' ]                   == assumed_role_user_id          # todo: add support for running in cache

        assert type(s3_client.list_buckets().get('Buckets')) is list




