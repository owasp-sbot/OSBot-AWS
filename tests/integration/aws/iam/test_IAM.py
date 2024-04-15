from unittest import TestCase

import pytest

from osbot_aws.testing.TestCase__Boto3_Cache import TestCase__Boto3_Cache
from osbot_utils.utils.Misc import list_set
from osbot_aws.AWS_Config           import AWS_Config
from osbot_aws.aws.iam.IAM          import IAM

IAM_USER_NAME__OSBOT_AWS = 'OSBot-AWS-Dev__Only-IAM'
TEST_USER_NAME           = 'test_user'
TEST_USER_ROLE           = 'test_role'

class Test_IAM(TestCase):
    account_id      : str
    aws_config      : AWS_Config
    current_user_arn: str
    iam             : IAM
    policy_document : str
    test_user       : str
    test_user_arn   : str
    test_role       : str


    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.aws_config       = AWS_Config()
        cls.account_id       = cls.aws_config.aws_session_account_id()
        cls.access_key_id    = cls.aws_config.aws_access_key_id()
        cls.current_user_arn = f'arn:aws:iam::{cls.account_id}:user/{IAM_USER_NAME__OSBOT_AWS}'
        cls.delete_created   = True
        cls.test_user        = TEST_USER_NAME
        cls.test_user_arn    = f'arn:aws:iam::{cls.account_id}:user/{cls.test_user}'
        cls.test_role        = TEST_USER_ROLE
        cls.test_role_arn    = f'arn:aws:iam::{cls.account_id}:role/{cls.test_role}'
        cls.policy_document  = {'Statement': [ { 'Action'   : 'sts:AssumeRole',
                                                 'Effect'   : 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}
        cls.iam = IAM(user_name=cls.test_user, role_name=cls.test_role)
        if cls.iam.user_exists() is False:
            cls.iam.user_create()
        if cls.iam.role_exists() is False:
            cls.iam.role_create(cls.policy_document)

    def test_policy_create__policy_delete__policy_details(self):
        policy_name     = 'test_policy'
        new_policy_document =  {    "Version": "2012-10-17",
                                    "Statement": [ { "Effect": "Allow",
                                                     "Action": "lambda:InvokeFunction",
                                                     "Resource": "arn:aws:lambda:*:*:function:*" }]}
        self.iam.policy_delete_by_name(policy_name)
        result              = self.iam.policy_create(policy_name, new_policy_document)
        expected_policy_arn = self.iam.policy_arn(policy_name)

        status     = result.get('status')
        policy_arn = result.get('policy_arn')

        assert status     == 'ok'
        assert policy_arn == expected_policy_arn

        assert self.iam.policy_info   (policy_arn).get('PolicyName'        ) == 'test_policy'
        assert self.iam.policy_details(policy_arn).get('policy_version').get('Document') == new_policy_document

        assert self.iam.policy_delete(policy_arn) is True

    # todo: move back to Cached section once we support capturing exceptions in boto3 cache
    def test_policy_name_exists(self):
        assert self.iam.policy_exists_by_name(policy_name='aaa'                                                               ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole'                                               ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole', policy_path='/service-role'                  ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole', policy_path='/service-role', account_id='aws') is True

    def test_role_create__and__delete(self):
        assert self.iam.role_delete() is True                                           # we already have this role from the setUpClass

        role = self.iam.role_create(self.policy_document)                               # create it again
        assert list_set(role) == ['Arn', 'AssumeRolePolicyDocument', 'CreateDate', 'Path', 'RoleId', 'RoleName']
        assert role.get('Arn'                     ) == self.test_role_arn
        assert role.get('Path'                    ) =='/'
        assert role.get('RoleName'                ) == self.test_role
        assert role.get('AssumeRolePolicyDocument') == self.policy_document
        assert self.iam.role_arn()                  == self.test_role_arn

    # todo: move back to Cached section once we support capturing exceptions in boto3 cache
    def test_user_exists(self):
        assert self.iam                      .user_exists() is True
        assert self.iam.set_user_name('aAAA').user_exists() is False

    # todo: move back to Cached section once we support capturing exceptions in boto3 cache
    def test_user_info(self):
        # user = self.iam.user_info()
        # assert user.get('Arn'     ) == self.test_user_arn
        # assert user.get('Path'    ) == '/'
        # assert user.get('UserName') ==self.test_user
        error_message = self.iam.set_user_name('AAAA').user_info()

        assert error_message.get('error' ) == 'An error occurred (NoSuchEntity) when calling the GetUser operation: The user with name AAAA cannot be found.'
        assert error_message.get('status') == 'error'
        exception = error_message.get('exception')
        assert exception.__class__.__name__ == 'NoSuchEntityException'
        assert error_message.get('exception')
        assert exception.operation_name == 'GetUser'
        assert exception.response.get('Error') == { 'Code'   : 'NoSuchEntity'                            ,
                                                    'Message': 'The user with name AAAA cannot be found.',
                                                    'Type'   : 'Sender'                                  }

    # todo: refactor all this into a helper class
    # def test_role_create_assume_role(self):
    #
    #     original_policy  = {'Statement': [ { 'Action'   : 'sts:AssumeRole',
    #                                          'Effect'   : 'Allow',
    #                                          'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}
    #
    #     new_policy       = {'Statement': [{'Action'   : 'sts:AssumeRole',
    #                                        'Effect'   : 'Allow',
    #                                        'Principal': {'AWS': self.current_user_arn } }, ]}
    #
    #     test_role        = IAM(role_name="temp_role_to_test_assume_role")
    #
    #     test_role.role_create(original_policy)
    #     role_arn              = test_role.role_arn()
    #     current_assume_policy = test_role.role_assume_policy()
    #
    #     test_role.role_assume_policy_update(new_policy)             # apply the new policy
    #
    #     sts               = STS()
    #     assumed_role_user = None
    #     credentials       = None
    #     for i in range(0,20):
    #         with Catch(log_exception=False):
    #             result = sts.assume_role(role_arn=role_arn)
    #             assumed_role_user = result.get('AssumedRoleUser')
    #             credentials       = result.get('Credentials')
    #             break
    #         wait(1)
    #     print(f'waited {i} seconds for the assume role')
    #     assert credentials is not None
    #     assert list_set(assumed_role_user) == ['Arn', 'AssumedRoleId']
    #     assert list_set(credentials      ) == ['AccessKeyId', 'Expiration', 'SecretAccessKey', 'SessionToken']
    #
    #
    #     #pprint(credentials)
    #
    #     # # this is how we can use these privs
    #     # credentials = sts.assume_role(role_arn=role_arn).get('Credentials')
    #     # aws_access_key_id = credentials.get('AccessKeyId')
    #     # aws_secret_access_key = credentials.get('SecretAccessKey')
    #     # aws_session_token = credentials.get('SessionToken')
    #     #
    #     # import boto3
    #     # session = boto3.Session(aws_access_key_id=aws_access_key_id,
    #     #                         aws_secret_access_key=aws_secret_access_key,
    #     #                         aws_session_token=aws_session_token)
    #     # pprint(session)
    #
    #
    #     aws_access_key_id = credentials.get('AccessKeyId')
    #     aws_secret_access_key = credentials.get('SecretAccessKey')
    #     aws_session_token = credentials.get('SessionToken')
    #
    #     try:
    #         import boto3
    #         session = boto3.Session(aws_access_key_id=aws_access_key_id,
    #                                 aws_secret_access_key=aws_secret_access_key,
    #                                 aws_session_token=aws_session_token)
    #
    #         iam_client = session.client('iam')
    #
    #         # Get the current user or role's details to retrieve associated policies
    #         user_or_role_name = session.client('sts').get_caller_identity().get('Arn')
    #
    #         # Assuming 'user_or_role_name' contains the role's ARN, parse it to get the role name
    #         role_name = user_or_role_name.split('/')[-1]
    #
    #         # List attached managed policies
    #         attached_policies = iam_client.list_attached_role_policies(RoleName=role_name)
    #         print("Attached Managed Policies:")
    #         for policy in attached_policies.get('AttachedPolicies', []):
    #             print(policy)
    #
    #         # List inline policies
    #         inline_policies = iam_client.list_role_policies(RoleName=role_name)
    #         print("\nInline Policies:")
    #         for policy_name in inline_policies.get('PolicyNames', []):
    #             policy_document = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)
    #             print(policy_document)
    #     except Exception as error:
    #         pprint(error)
    #
    #     # assert sts.assume_role(role_arn=role_arn).get('Credentials') is not None
    #     # test_role.role_assume_policy_update(current_assume_policy)
    #     # assert test_role.role_assume_policy() == current_assume_policy
    #     # test_role.role_delete()  # delete the temp role created


