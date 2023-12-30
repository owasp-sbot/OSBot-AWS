import os
from unittest import TestCase

import pytest
import unittest
from osbot_utils.testing.Catch      import Catch
from osbot_utils.utils.Misc import wait, list_set
from osbot_aws.AWS_Config           import AWS_Config
from osbot_aws.aws.iam.IAM          import IAM
from osbot_aws.aws.iam.STS          import STS
from osbot_aws.helpers.Test_Helper  import Test_Helper
from osbot_utils.utils.Assert       import Assert
from osbot_utils.utils.Dev          import pprint


# todo: refactor this into the test class

IAM_USER_NAME__OSBOT_AWS = 'OSBot-AWS-Dev__Only-IAM'
TEST_USER_NAME           = 'test_user'
TEST_USER_ROLE           = 'test_role'

class Test_IAM(TestCase):
    account_id      : str
    aws_config      : AWS_Config
    policy_document : str
    test_user       : str
    test_role       : str


    @classmethod
    def setUpClass(cls):
        cls.aws_config       = AWS_Config()
        cls.account_id       = cls.aws_config.aws_session_account_id()
        cls.access_key_id    = cls.aws_config.aws_access_key_id()
        cls.delete_created   = True
        cls.test_user        = TEST_USER_NAME
        cls.test_user_arn    = f'arn:aws:iam::{cls.account_id}:user/{cls.test_user}'
        cls.test_role        = TEST_USER_ROLE
        cls.test_role_arn    = f'arn:aws:iam::{cls.account_id}:role/{cls.test_role}'
        cls.policy_document  = {'Statement': [ { 'Action'   : 'sts:AssumeRole',
                                                 'Effect'   : 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}
        iam = IAM(user_name=cls.test_user, role_name=cls.test_role)
        if iam.user_exists() is False:
            iam.user_create()
        if iam.role_exists() is False:
            iam.role_create(cls.policy_document)

    # @classmethod
    # def tearDownClass(cls):
    #     if delete_created:
    #         iam = IAM(user_name=test_user,role_name=test_role)
    #         iam.user_delete()
    #         assert iam.user_exists() is False
    #         iam.role_delete()
    #         assert iam.role_exists() is False
    #         assert iam.role_arn()    is None

    def setUp(self):
        #logging.getLogger().addHandler(logging.StreamHandler())
        self.iam = IAM(user_name=self.test_user,role_name=self.test_role )

    def test__setup(self):
        assert self.account_id
        assert self.access_key_id
        assert self.iam.user_exists() is True
        assert self.iam.role_exists() is True
        assert self.test_user         == TEST_USER_NAME
        assert self.test_user_arn     == f'arn:aws:iam::{self.account_id}:user/{self.test_user}'
        assert self.test_role         == TEST_USER_ROLE
        assert self.test_role_arn     == f'arn:aws:iam::{self.account_id}:role/{self.test_role}'


    def test_access_keys(self):
        access_keys = self.iam.access_keys(index_by='AccessKeyId')
        access_key  = access_keys[self.access_key_id]
        assert len(access_keys) == 1
        assert list_set(access_key.keys()) == ['AccessKeyId', 'CreateDate', 'Status', 'UserName']
        assert access_key.get('AccessKeyId') == self.access_key_id
        assert access_key.get('Status'     ) == 'Active'
        assert access_key.get('UserName'   ) == IAM_USER_NAME__OSBOT_AWS

    def test_caller_identity(self):
        caller_identity = self.iam.caller_identity()
        assert list_set           (caller_identity) == ['Account', 'Arn', 'UserId']
        assert caller_identity.get('Account'      ) == self.account_id
        assert caller_identity.get('Arn'          ) == f'arn:aws:iam::{self.account_id}:user/{IAM_USER_NAME__OSBOT_AWS}'
        assert caller_identity.get('UserId'       ) != self.access_key_id  # todo find place where I can get the user id (which is different from the access key id)



@pytest.mark.skip('Wire up tests')
class Test_IAM___TO_WIRE_UP(TestCase):

    # ------ tests ------




    @pytest.mark.skip('Fix test')
    def test_groups(self):
        assert len(self.iam.groups()) > 5

    def test_policies(self):
        assert len(self.iam.policies())  > 500

    def test_policy_arn(self):
        assert self.iam.policy_arn('aaa'          ) == 'arn:aws:iam::{0}:policy/aaa'    .format(account_id)
        assert self.iam.policy_arn('aaa/bbb'      ) == 'arn:aws:iam::{0}:policy/aaa/bbb'.format(account_id)
        assert self.iam.policy_arn('aa','/bb'     ) == 'arn:aws:iam::{0}:policy/bb/aa'  .format(account_id)
        assert self.iam.policy_arn('aa','/bb','cc') == 'arn:aws:iam::cc:policy/bb/aa'
        assert self.iam.policy_arn(None)      is None

    def test_policy_create__policy_delete__policy_details(self):
        policy_name     = 'test_policy'
        self.iam.policy_delete_by_name(policy_name)
        new_policy_document =  {    "Version": "2012-10-17",
                                    "Statement": [ { "Effect": "Allow",
                                                     "Action": "lambda:InvokeFunction",
                                                     "Resource": "arn:aws:lambda:*:*:function:*" }]}
        result              = self.iam.policy_create(policy_name, new_policy_document)
        expected_policy_arn = self.iam.policy_arn(policy_name)

        status     = result.get('status')
        policy_arn = result.get('policy_arn')

        assert status     == 'ok'
        assert policy_arn == expected_policy_arn

        assert self.iam.policy_info   (policy_arn).get('PolicyName'        ) == 'test_policy'
        assert self.iam.policy_details(policy_arn).get('policy_version').get('Document') == new_policy_document

        assert self.iam.policy_delete(policy_arn) is True


    def test_policy_name_exists(self):
        assert self.iam.policy_exists_by_name('aaa'                                        ) is False
        assert self.iam.policy_exists_by_name('AWSBatchServiceRole'                        ) is False
        assert self.iam.policy_exists_by_name('AWSBatchServiceRole','/service-role'        ) is False
        assert self.iam.policy_exists_by_name('AWSBatchServiceRole', '/service-role', 'aws') is True


    def test_policy_info(self):
        assert self.iam.policy_info('AAAAAA') is None

    #def test_user_create(self):                # convered in setUpClass
    #    self.iam.user_create()

    #def test_user_delete(self):                # convered in tearDownClass
    #    Dev.pprint(self.iam.user_delete())

    def test_user_exists(self):
        assert self.iam                      .user_exists() is True
        assert self.iam.set_user_name('aAAA').user_exists() is False

    def test_user_info(self):
        user = self.iam.user_info()
        (
            Assert(user).field_is_equal('Arn'     , test_user_arn)
                        .field_is_equal('Path'    , '/')
                        .field_is_equal('UserName', test_user)
        )
        assert self.iam.set_user_name('AAAA').user_info().get('error') is not None

    def test_users(self):
        assert len(list(self.iam.users()))  > 5

    def test_role_create(self):
        self.iam.role_delete()
        role = self.iam.role_create(policy_document)
        (
            Assert(role).field_is_equal('Arn'                     ,test_role_arn)
                        .field_is_equal('Path'                    ,'/')
                        .field_is_equal('RoleName'                , test_role)
                        .field_is_equal('AssumeRolePolicyDocument', policy_document)
        )
        assert self.iam.role_arn() == test_role_arn

    def test_role_create_assume_role(self):
        sts = STS()
        current_user_arn = sts.caller_identity_arn()
        original_policy  = {'Statement': [ { 'Action'   : 'sts:AssumeRole',
                                             'Effect'   : 'Allow',
                                             'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}

        new_policy       = {'Statement': [{'Action'   : 'sts:AssumeRole',
                                           'Effect'   : 'Allow',
                                           'Principal': {'AWS': current_user_arn } }]}

        test_role        = IAM(role_name="temp_role_to_test_assume_role")

        test_role.role_create(original_policy)
        role_arn              = test_role.role_arn()

        current_assume_policy = test_role.role_assume_policy()
        test_role.role_assume_policy_update(new_policy)

        for i in range(0,15):
            with Catch(log_exception=False):
                sts.assume_role(role_arn=role_arn)
                sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)
                # sts.assume_role(role_arn=role_arn)

                pprint('got credentials')
                break
            print(f'after {i} seconds')
            wait(1)

        assert sts.assume_role(role_arn=role_arn).get('Credentials') is not None
        test_role.role_assume_policy_update(current_assume_policy)
        assert test_role.role_assume_policy() == current_assume_policy
        test_role.role_delete()

        # credentials = sts.assume_role(role_arn=role_arn).get('Credentials')
        # aws_access_key_id = credentials.get('AccessKeyId')
        # aws_secret_access_key = credentials.get('SecretAccessKey')
        # aws_session_token = credentials.get('SessionToken')
        #
        # import boto3
        # session = boto3.Session(aws_access_key_id=aws_access_key_id,
        #                         aws_secret_access_key=aws_secret_access_key,
        #                         aws_session_token=aws_session_token)

    def test_role_info(self):
        role = self.iam.set_role_name(test_role).role_info()                # also tests the set_role_name function
        assert role.get('Arn'     ) == test_role_arn
        assert role.get('RoleName') == test_role

    @pytest.mark.skip('Fix test')
    def test_role_policies(self):
        policies = self.iam.role_policies()
        assert len(set(policies)) == 0

        iam = IAM(role_name='AWSServiceRoleForAPIGateway')
        assert iam.role_policies() == {'APIGatewayServiceRolePolicy': 'arn:aws:iam::aws:policy/aws-service-role/APIGatewayServiceRolePolicy'}
        assert len(iam.role_policies_statements().get('APIGatewayServiceRolePolicy')[0].get('Action')) > 10

    def test_role_policies_attach__role_policies_detach(self):
        policy_name = 'test_policy'
        policy_document = {"Version": "2012-10-17",                                     # refactor this with policy helper
                           "Statement": [{  "Effect": "Allow",
                                            "Action": "lambda:InvokeFunction",
                                            "Resource": "arn:aws:lambda:*:*:function:*"}]}
        policy_arn = self.iam.policy_create(policy_name, policy_document).get('policy_arn')

        assert len(list(self.iam.role_policies())) == 0
        self.iam.role_policy_attach(policy_arn)
        assert list(self.iam.role_policies())      == ['test_policy']
        self.iam.role_policy_detach(policy_arn)

        assert self.iam.policy_exists(policy_arn) is True
        assert self.iam.policy_delete(policy_arn) is True          # this will not delete a policy that is attached
        assert self.iam.policy_exists(policy_arn) is False

    #@pytest.mark.skip('Fix test')
    def test_roles(self):
        assert len(self.iam.roles())  > 5

    def test_user_access_key_create__delete(self):
        access_key = self.iam.user_access_key_create()
        assert self.iam.access_key__wait_until_key_is_working    (access_key,success_count=1) is True
        self.iam.user_access_keys_delete_all()
        assert self.iam.access_key__wait_until_key_is_not_working(access_key, success_count=1) is True

    # test below was using to get some stats on when the key is enabled
    # def test_user_access_key_create__delete(self):
    #     print()
    #     access_key = self.iam.user_access_key_create()
    #     assert access_key.get('UserName') == test_user
    #     assert len(self.iam.user_access_keys()) > 0
    #     assert self.iam.access_key__wait_until_key_is_working(access_key) is True
    #     print('*******')
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print('-------')
    #     assert self.iam.user_access_keys_delete_all() is True
    #     print('#######')
    #     assert self.iam.access_key__wait_until_key_is_not_working(access_key) is True
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))
    #     print(self.iam.access_key__is_key_working(access_key))




