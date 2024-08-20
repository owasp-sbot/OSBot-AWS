import os

from osbot_aws.AWS_Config                       import AWS_Config
from osbot_aws.aws.iam.IAM                      import IAM
from osbot_aws.testing.TestCase__Boto3_Cache    import TestCase__Boto3_Cache
from osbot_utils.testing.Logging import Logging
from osbot_utils.utils.Misc                     import list_set
from osbot_utils.utils.Python_Logger import Python_Logger
from tests.integration.aws.iam.test_IAM         import IAM_USER_NAME__OSBOT_AWS, TEST_USER_NAME, TEST_USER_ROLE

class test_IAM__Cached(TestCase__Boto3_Cache):
    account_id      : str
    aws_config      : AWS_Config
    current_user_arn: str
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
        iam = IAM(user_name=cls.test_user, role_name=cls.test_role)
        if iam.user_exists() is False:
            iam.user_create()
        if iam.role_exists() is False:
            iam.role_create(cls.policy_document)

    def setUp(self):
        #logging.getLogger().addHandler(logging.StreamHandler())
        self.iam = IAM(user_name=self.test_user,role_name=self.test_role )         # get a new object for each test

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
        assert caller_identity.get('Arn'          ) == self.current_user_arn
        assert caller_identity.get('UserId'       ) != self.access_key_id  # todo find place where I can get the user id (which is different from the access key id)

    def test_groups(self):
        groups = self.iam.groups()
        for group in groups:
            assert list_set(group) == ['Arn', 'CreateDate', 'GroupId', 'GroupName', 'Path']

    # todo: move to Unit tests
    def test_policy_arn(self):
        assert self.iam.policy_arn(policy_name='aaa'                                    ) == f'arn:aws:iam::{self.account_id}:policy/aaa'
        assert self.iam.policy_arn(policy_name='aaa/bbb'                                ) == f'arn:aws:iam::{self.account_id}:policy/aaa/bbb'
        assert self.iam.policy_arn(policy_name='aa',policy_path='/bb'                   ) == f'arn:aws:iam::{self.account_id}:policy/bb/aa'
        assert self.iam.policy_arn(policy_name='aa',policy_path='/bb',account_id='cc'   ) == f'arn:aws:iam::cc:policy/bb/aa'
        assert self.iam.policy_arn(policy_name=None                                     )      is None

    def test_policy_info(self):
        assert self.iam.policy_info('AAAAAA') is None

    def test_policy_name_exists(self):
        assert self.iam.policy_exists_by_name(policy_name='aaa'                                                               ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole'                                               ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole', policy_path='/service-role'                  ) is False
        assert self.iam.policy_exists_by_name(policy_name='AWSBatchServiceRole', policy_path='/service-role', account_id='aws') is True


    def test_policies(self):
        for policy in self.iam.policies():
            assert list_set(policy) == ['Arn', 'AttachmentCount', 'CreateDate', 'DefaultVersionId', 'IsAttachable', 'Path', 'PermissionsBoundaryUsageCount','PolicyId', 'PolicyName', 'UpdateDate']
            break
        #pprint(count)   # DC: last time I executed this there were 1183 polices

    def test_user_exists(self):
        assert self.iam                      .user_exists() is True
        assert self.iam.set_user_name('aAAA').user_exists() is False

    def test_user_info(self):
        user = self.iam.user_info()
        assert user.get('Arn'     ) == self.test_user_arn
        assert user.get('Path'    ) == '/'
        assert user.get('UserName') ==self.test_user

    def test_user_info___with_bad_user(self):
        error_message = self.iam.set_user_name('AAAA').user_info()
        exception     = error_message.get('exception')

        assert error_message.get('error' ) == 'An error occurred (NoSuchEntity) when calling the GetUser operation: The user with name AAAA cannot be found.'
        assert error_message.get('status') == 'error'
        assert error_message.get('exception')
        assert exception.operation_name == 'GetUser'
        assert exception.response.get('Error') == { 'Code'   : 'NoSuchEntity'                            ,
                                                    'Message': 'The user with name AAAA cannot be found.',
                                                    'Type'   : 'Sender'                                  }
    def test_users(self):
        for user in self.iam.users():
            assert list_set(user) == ['Arn', 'CreateDate', 'Path', 'UserId', 'UserName']
            break


