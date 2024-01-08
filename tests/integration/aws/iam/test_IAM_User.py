import pytest

from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.utils.Misc import list_set, random_password

from osbot_utils.base_classes.Kwargs_To_Disk import Kwargs_To_Disk
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

from osbot_utils.utils.Dev import pprint

from osbot_utils.helpers.Local_Cache import Local_Cache

from osbot_aws.aws.iam.IAM_User         import IAM_User
from osbot_aws.helpers.Test_Helper      import Test_Helper

#@pytest.mark.skip('Fix tests')
#@pytest.mark.skip('Wire up tests')

class Local_Test_Data(Kwargs_To_Disk):
    _user       : IAM_User
    setup       : bool
    user_exists : bool
    user_info   : dict
    user_name   : str

    def __init__(self):
        super().__init__()
        self.setup_user()

    def user_id(self):
        return self.user_info.get('UserId')

    def setup_user(self):
        #data = self.local_cache.data()
        if self.user_name is None:
            self.user_name   = 'OSBot__Unit_Test_User'
            self.setup = False

        self._user       = IAM_User(self.user_name)

        if self.user_exists is not True:
            self.user_info  = self._user.create()
            self.user_exists = self._user.exists()
            self.setup = True
        #self.local_cache.set('user_name', self.user_name)

        #print(self.user.exists())

class test_IAM_User(Test_Helper):

    def setUp(self):
        self.asw_config = AWS_Config()
        super().setUp()
        self.user_name = 'OSBot__Unit_Test_User'
        self.test_data = Local_Test_Data()
        self.user      = IAM_User(self.user_name)

    # def tearDown(self):
    #     self.test_data._cache_delete()

    def test__test_data(self):
        expected_user_name = 'OSBot__Unit_Test_User'
        with self.test_data as _:
            cache_data = _._cache_data()
            user_info  = _.user_info
            assert list_set(cache_data) == ['setup', 'user_exists', 'user_info', 'user_name']
            assert _.setup                 is True
            assert _.user_exists           is True
            assert _.user_name             == expected_user_name
            assert user_info.get('Arn'     ) == f'arn:aws:iam::{self.asw_config.account_id()}:user/{expected_user_name}'
            assert user_info.get('Path'    ) == '/'
            assert user_info.get('UserId'  ) == _.user_id()
            assert user_info.get('UserName') == expected_user_name

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
