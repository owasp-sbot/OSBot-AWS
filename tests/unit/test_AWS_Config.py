import os
from unittest import TestCase

from osbot_aws.AWS_Config import AWS_Config


class test_AWS_Config(TestCase):
    def setUp(self) -> None:
        self.aws_config = AWS_Config()

    def test_environment_variables_setup(self):
        def check_env_value(helper_method, env_name):
            value = helper_method()
            assert type(value) == str
            assert value       != ""
            assert value       == os.getenv(env_name)

        check_env_value(self.aws_config.aws_session_profile_name, 'AWS_PROFILE_NAME'          )
        check_env_value(self.aws_config.aws_session_region_name , 'AWS_DEFAULT_REGION'        )
        check_env_value(self.aws_config.aws_session_account_id  , 'AWS_ACCOUNT_ID'            )
        check_env_value(self.aws_config.lambda_s3_bucket        , 'OSBOT_LAMBDA_S3_BUCKET'    )
        check_env_value(self.aws_config.lambda_s3_key_prefix    , 'OSBOT_LAMBDA_S3_KEY_PREFIX')
        check_env_value(self.aws_config.lambda_role_name        , 'OSBOT_LAMBDA_ROLE_NAME'    )
        check_env_value(self.aws_config.bot_name                , 'OSBOT_NAME'                )

