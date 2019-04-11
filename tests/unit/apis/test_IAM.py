import sys; sys.path.append('..')
import unittest
from unittest import TestCase

from pbx_gs_python_utils.utils.Assert import Assert
from pbx_gs_python_utils.utils.Dev import Dev

from osbot_aws.apis.IAM import IAM
from osbot_aws.Globals import Globals


account_id       = '244560807427'
delete_created   = True
test_user        = 'test_user'
test_user_arn    = 'arn:aws:iam::{0}:user/test_user'.format(account_id)
test_role        = 'test_role'
test_role_arn    = 'arn:aws:iam::{0}:role/test_role'.format(244560807427)
policy_document  = {'Statement': [ { 'Action': 'sts:AssumeRole',
                                                 'Effect': 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}


class Test_IAM(TestCase):

    @classmethod
    def setUpClass(cls):
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")

        iam = IAM(user_name=test_user, role_name=test_role)
        if iam.user_exists() is False:
            iam.user_create()
        if iam.role_exists() is False:
            iam.role_create(policy_document)

    @classmethod
    def tearDownClass(cls):
        if delete_created:
            iam = IAM(user_name=test_user,role_name=test_role)
            iam.user_delete()
            assert iam.user_exists() is False
            iam.role_delete()
            assert iam.role_exists() is False
            assert iam.role_arn()    is None

    def setUp(self):
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.iam = IAM(user_name=test_user,role_name=test_role )

    @unittest.skip
    def test_account_id(self):
        assert type(self.iam.account_id()) is str
        account_id_1 = self.iam.account_id()
        Globals.aws_session_profile_name='gs-detect-aws'
        self.iam._account_id = None
        self.iam._sts        = None
        account_id_2 = self.iam.account_id()
        assert account_id_1 != account_id_2
        Globals.aws_session_profile_name = 'default'



    # def test_assume_role(self):       # getting `(AccessDenied) when calling the AssumeRole operation: Access denied`
    #     role_arn          = 'arn:aws:iam::244560807427:role/temp_role_for_lambda_invocation'  # needs to be non account_id specific
    #     role_session_name = 'temp_role_for_test'
    #     Dev.pprint(self.iam.assume_role(role_arn,role_session_name))

    def test_caller_identity(self):
        assert set(self.iam.caller_identity()) == {'UserId', 'Account', 'Arn'}

    def test_groups(self):
        assert len(self.iam.groups()) > 5

    def test_policies(self):
        assert len(self.iam.policies())  > 500

    def test_policy_arn(self):
        #account_id = self.iam.account_id()
        assert self.iam.policy_arn('aaa'          ) == 'arn:aws:iam::{0}:policy/aaa'    .format(account_id)
        assert self.iam.policy_arn('aaa/bbb'      ) == 'arn:aws:iam::{0}:policy/aaa/bbb'.format(account_id)
        assert self.iam.policy_arn('aa','/bb'     ) == 'arn:aws:iam::{0}:policy/bb/aa'  .format(account_id)
        assert self.iam.policy_arn('aa','/bb','cc') == 'arn:aws:iam::cc:policy/bb/aa'
        assert self.iam.policy_arn(None)      is None

        self.iam.set_account_id('12345')
        assert self.iam.policy_arn('aaa'    ) == 'arn:aws:iam::{0}:policy/aaa'    .format('12345')

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

    #def test_user_create(self):
    #    self.iam.user_create()

    #def test_user_delete(self):
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
        assert self.iam.set_user_name('AAAA').user_info() is None

    def test_users(self):
        assert len(self.iam.users())  > 10

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

    def test_role_info(self):
        role = self.iam.set_role_name(test_role).role_info()                # also tests the set_role_name function
        assert role.get('Arn'     ) == test_role_arn
        assert role.get('RoleName') == test_role

    def test_role_policies(self):
        policies = self.iam.role_policies()
        assert len(set(policies)) == 0

    def test_role_policies(self):
        iam = IAM(role_name='AWSBatchServiceRole')
        assert iam.role_policies() == {'AWSBatchServiceRole': 'arn:aws:iam::aws:policy/service-role/AWSBatchServiceRole'}
        assert len(iam.role_policies_statements().get('AWSBatchServiceRole')[0].get('Action')) == 59

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

    def test_roles(self):
        assert len(self.iam.roles())  > 70

