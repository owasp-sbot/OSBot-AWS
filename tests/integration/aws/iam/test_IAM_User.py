from unittest import TestCase
import pytest
from osbot_aws.AWS_Config                                   import AWS_Config
from osbot_utils.utils.Misc                                 import random_password
from osbot_aws.aws.iam.IAM_User                             import IAM_User
from tests.integration._caches.OSBot__Unit_Test_User import OSBot__Unit_Test_User

class test_IAM_User(TestCase):
    user_name : str

    @classmethod
    def setUp(cls):
        cls.asw_config = AWS_Config()
        cls.user_name = 'OSBot__Unit_Test_User'
        cls.test_data = OSBot__Unit_Test_User()
        cls.user      = IAM_User(cls.user_name)

    # def tearDown(self):
    #     self.test_data._cache_delete()

    def test_arn(self):
        self.result = self.user.arn()

    @pytest.mark.skip('refactor to use a temp user name, i.e. not the main one used for the other tests')
    def test_create_exists_delete(self):
        assert self.user.create().get('UserName') == self.user_name
        assert self.user.exists() is True
        assert self.user.delete() is True
        assert self.user.exists() is False

    def test_access_keys(self):
        result = self.user.access_keys()
        assert result == []

    def test_groups(self):
        result = self.user.groups(index_by='group_name')
        assert result == {}

    def test_user_id(self):
        assert self.user.user_id() == self.test_data.user_id()

    def test_info(self):
        cache_user_info = self.test_data.user_info
        result          = self.user.info()
        result['create_date']  = str(result.get('create_date'))
        assert result == { 'arn'                 : cache_user_info.get('Arn'        ),
                           'create_date'         : cache_user_info.get('CreateDate' ),
                           'password_last_used'  : None,
                           'path'                : cache_user_info.get('Path'       ),
                           'permissions_boundary': None,
                           'tags'                : None,
                           'user_id'             : cache_user_info.get('UserId'     ),
                           'user_name'           : cache_user_info.get('UserName'   )}

    def test_policies(self):
        assert self.user.policies() == []

    def test_set_password(self):

        result = self.user.set_password(random_password(), reset_required=False)
        if result.get('error'):         # todo: figure out why this test returns this error the 2nd time
            assert result.get('error') == 'An error occurred (EntityAlreadyExists) when calling the ' \
                                          'CreateLoginProfile operation: Login Profile for user '     \
                                          'OSBot__Unit_Test_User already exists.'

    # def test_roles(self):
    #     roles = self.user.roles()
    #
    #     pprint(roles)

    def test_tags(self):
        assert self.user.tags() is None
