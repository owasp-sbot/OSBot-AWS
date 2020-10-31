import unittest

from osbot_aws.helpers.Test_Helper import Test_Helper
from osbot_aws.apis.IAM import IAM
from osbot_aws.Globals import Globals
from osbot_utils.utils.Assert import Assert

account_id       = Globals.aws_session_account_id
delete_created   = True
test_user        = 'test_user'
test_user_arn    = 'arn:aws:iam::{0}:user/test_user'.format(account_id)
test_role        = 'test_role'
test_role_arn    = 'arn:aws:iam::{0}:role/test_role'.format(account_id)
policy_document  = {'Statement': [ { 'Action': 'sts:AssumeRole',
                                                 'Effect': 'Allow',
                                                 'Principal': { 'Service': 'codebuild.amazonaws.com'}}]}


class Test_IAM(Test_Helper):        # todo move Test_Helper into this OSBOT_AWS


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
        super().setUp()
        import warnings
        warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>")
        self.iam = IAM(user_name=test_user,role_name=test_role )

    # ------ tests ------

    @unittest.skip("Doesn't work in CodeBuild since there is only one configuration in there")
    def test_account_id(self):
        account_id_1 = self.iam.account_id('gs-detect-aws')
        assert Globals.aws_session_profile_name == 'gs-detect-aws'

        self.iam._account_id = None
        self.iam._sts        = None

        account_id_2 = self.iam.account_id('default')
        assert Globals.aws_session_profile_name == 'default'
        assert account_id_1 != account_id_2

        self.iam._account_id = None
        self.iam._sts = None

        account_id_3 = self.iam.account_id()
        assert Globals.aws_session_profile_name == 'default'
        assert account_id_2 == account_id_3

    def test_access_keys(self):
        assert len(self.iam.access_keys(index_by='AccessKeyId')) > 0
        assert len(self.iam.access_keys(group_by='UserName'   )) > 0

    def test_caller_identity(self):
        assert set(self.iam.caller_identity()) == {'UserId', 'Account', 'Arn'}

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

    def test_role_info(self):
        role = self.iam.set_role_name(test_role).role_info()                # also tests the set_role_name function
        assert role.get('Arn'     ) == test_role_arn
        assert role.get('RoleName') == test_role

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

    def test_roles(self):
        assert len(self.iam.roles())  > 70

    def test_user_access_key_create__delete(self):
        access_key = self.iam.user_access_key_create()
        assert self.iam.access_key__wait_until_key_is_working(access_key,success_count=1) is True
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




