import re
from unittest                                        import TestCase
from osbot_aws.testing.Temp__Random__AWS_Credentials import Temp__Random__AWS_Credentials
from osbot_utils.utils.Env                           import get_env, set_env, del_env
from osbot_utils.utils.Misc                          import random_text


class test_Temp__Random__AWS_Credentials(TestCase):

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

        with Temp__Random__AWS_Credentials() as _:
            aws_access_key_id       = get_env('AWS_ACCESS_KEY_ID')
            aws_secret_access_key   = get_env('AWS_SECRET_ACCESS_KEY')
            aws_account_id          = get_env('AWS_ACCOUNT_ID')
            aws_default_region      = get_env('AWS_DEFAULT_REGION')

            assert re.match(r'^AKIA[0-9A-Z]{16}$', aws_access_key_id)                   # Validate the generated AWS_ACCESS_KEY_ID format (AKIA followed by 16 uppercase letters/digits)
            assert re.match(r'^[A-Za-z0-9/+=]{40}$', aws_secret_access_key)             # Validate the generated AWS_SECRET_ACCESS_KEY format (40 characters, mixed case, digits, special chars)
            assert re.match(r'^\d{12}$', aws_account_id)                                # Validate the generated AWS_ACCOUNT_ID format (12 digits)


            assert aws_default_region in [ 'us-east-1'     , 'us-west-1'   , 'us-west-2'     ,  # Validate the generated AWS_DEFAULT_REGION is one of the common AWS regions
                                           'eu-west-1'     , 'eu-central-1', 'ap-southeast-1',
                                           'ap-northeast-1', 'ap-south-1'  , 'sa-east-1'     ]


        assert get_env('AWS_ACCESS_KEY_ID') == self.temp_value__AWS_ACCESS_KEY_ID


