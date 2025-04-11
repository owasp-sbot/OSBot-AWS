import pytest
from unittest                                        import TestCase
from osbot_aws.AWS_Config                            import AWS_Config
from osbot_aws.testing.Pytest                        import skip_pytest___aws_pytest_user_name__is_not_set
from tests.integration._caches.OSBot__Unit_Test_User import OSBot__Unit_Test_User, OSBOT__TEST__USER_NAME


class test_OSBot__Unit_Test_User(TestCase):

    @classmethod
    def setUpClass(cls):
        skip_pytest___aws_pytest_user_name__is_not_set()

    def setUp(self):
        self.aws_config = AWS_Config()
        self.test_data  = OSBot__Unit_Test_User()

    def test_setup_user(self):
        expected_user_name = OSBOT__TEST__USER_NAME
        with self.test_data as _:
            cache_data = _._cache_data()
            user_info  = _.user_info
            assert _._cache_exists()       is True
            assert _.setup                 is True
            assert _.user_exists           is True
            assert _.user_name             == expected_user_name
            assert user_info.get('Arn'     ) == f'arn:aws:iam::{self.aws_config.account_id()}:user/{expected_user_name}'
            assert user_info.get('Path'    ) == '/'
            assert user_info.get('UserId'  ) == _.user_id()
            assert user_info.get('UserName') == expected_user_name