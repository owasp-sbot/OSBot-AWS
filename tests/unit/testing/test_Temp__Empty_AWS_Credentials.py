from unittest import TestCase

from osbot_aws.testing.Temp__Empty_AWS_Credentials import Temp__Empty_AWS_Credentials
from osbot_utils.utils.Env import get_env, set_env, del_env
from osbot_utils.utils.Misc import random_text


class test_Temp__Empty_AWS_Credentials(TestCase):

    def setUp(self):
        self.current_value__AWS_ACCESS_KEY_ID = get_env('AWS_ACCESS_KEY_ID')
        self.temp_value__AWS_ACCESS_KEY_ID    = random_text()

        set_env('AWS_ACCESS_KEY_ID', self.temp_value__AWS_ACCESS_KEY_ID)

    def tearDown(self):
        if self.current_value__AWS_ACCESS_KEY_ID is None:
            del_env('AWS_ACCESS_KEY_ID')
        else:
            set_env('AWS_ACCESS_KEY_ID', self.current_value__AWS_ACCESS_KEY_ID)

    def test__context(self):
        assert get_env('AWS_ACCESS_KEY_ID') == self.temp_value__AWS_ACCESS_KEY_ID
        with Temp__Empty_AWS_Credentials() as _:
            assert get_env('AWS_ACCESS_KEY_ID') == ''

            assert _.env_vars == dict(AWS_ACCESS_KEY_ID     = '',
                                      AWS_SECRET_ACCESS_KEY = '',
                                      AWS_ACCOUNT_ID        = '',
                                      AWS_DEFAULT_REGION    = '')
        assert get_env('AWS_ACCESS_KEY_ID') == self.temp_value__AWS_ACCESS_KEY_ID


