import unittest
from unittest import TestCase

from utils.Assert import Assert
from utils.Dev import Dev
from pbx_gs_python_utils.utils.aws.IAM import IAM

delete_created   = True
test_user        = 'test_user'
test_user_arn    = 'arn:aws:iam::244560807427:user/test_user'
test_role        = 'test_role'
test_role_arn    = 'arn:aws:iam::244560807427:role/test_role'
policy_document  = {'Statement': [ { 'Action': 'sts:AssumeRole',
                                                 'Effect': 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}

class Test_IAM(TestCase):

    @classmethod
    def setUpClass(cls):
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

    def setUp(self):
        self.iam = IAM(user_name=test_user,role_name=test_role )

    def test_groups(self):
        assert len(self.iam.groups()) > 5

    @unittest.skip
    def test_policies(self):
        assert len(self.iam.policies())  > 500

    def test_policy_create__policy_delete(self):
        policy_name     = 'test_policy'
        policy_document =  {    "Version": "2012-10-17",
                                "Statement": [ {
                                                    "Sid": "VisualEditor0",
                                                    "Effect": "Allow",
                                                    "Action": "lambda:InvokeFunction",
                                                    "Resource": "arn:aws:lambda:*:*:function:*" }]}
        Dev.pprint(self.iam.policy_create(policy_name, policy_document))
        assert self.iam.policy_delete(policy_name) is True

    def test_policy_info(self):
        assert self.iam.policy_info('test_policy').get('PolicyName') == 'test_policy'
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

    def test_role_info(self):
        role = self.iam.set_role_name('gsbot-code-build-service').role_info()
        Dev.pprint(role)

    def test_role_policies(self):
        #policies = self.iam.role_policies()
        policies = self.iam.set_role_name('gsbot-code-build-service').role_policies()
        Dev.pprint(set(policies))

    def test_roles(self):
        assert len(self.iam.roles())  > 70

