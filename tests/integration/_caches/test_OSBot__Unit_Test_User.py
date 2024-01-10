from unittest import TestCase

from osbot_aws.AWS_Config import AWS_Config
from osbot_utils.utils.Misc import list_set

from tests.integration._caches.OSBot__Unit_Test_User import OSBot__Unit_Test_User, OSBOT__TEST__USER_NAME


class test_OSBot__Unit_Test_User(TestCase):

    def setUp(self):
        self.asw_config = AWS_Config()
        self.test_data  = OSBot__Unit_Test_User()

    def test_setup_user(self):
        expected_user_name = OSBOT__TEST__USER_NAME
        with self.test_data as _:
            cache_data = _._cache_data()
            user_info  = _.user_info
            assert list_set(cache_data) == ['abc',
                                             'access_keys',
                                             'data__access_keys',
                                             'setup',
                                             'user_data',
                                             'user_exists',
                                             'user_info',
                                             'user_name']
            assert _._cache_exists()       is True
            assert _.setup                 is True
            assert _.user_exists           is True
            assert _.user_name             == expected_user_name
            assert user_info.get('Arn'     ) == f'arn:aws:iam::{self.asw_config.account_id()}:user/{expected_user_name}'
            assert user_info.get('Path'    ) == '/'
            assert user_info.get('UserId'  ) == _.user_id()
            assert user_info.get('UserName') == expected_user_name