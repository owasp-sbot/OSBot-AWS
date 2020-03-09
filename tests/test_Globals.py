import os
from unittest import TestCase

class test_Globals(TestCase):

    def test_static_values(self):
        from osbot_aws.Globals import Globals
        assert Globals.aws_session_profile_name == 'gw-bot'
        assert Globals.aws_session_region_name  == 'eu-west-1'
        assert Globals.aws_session_account_id   == '311800962295'
        assert Globals.bot_name                 == 'gw_bot'
        assert Globals.lambda_s3_bucket         == 'gw-bot-lambdas'
        assert Globals.lambda_s3_key_prefix     == 'lambdas'
        assert Globals.lambda_layers_s3_bucket  == 'gw-bot-lambda-layers'
        assert Globals.lambda_role_name         == 'gwbot-lambdas-temp'

    def test_environment_variables(self):
        os.environ['AWS_PROFILE_NAME'               ] = 'AWS_PROFILE_NAME'
        os.environ['AWS_REGION_NAME'                ] = 'AWS_REGION_NAME'
        os.environ['AWS_ACCOUNT_ID'                 ] = 'AWS_ACCOUNT_ID'
        os.environ['OSBOT_LAMBDA_S3_BUCKET'         ] = 'OSBOT_LAMBDA_S3_BUCKET'
        os.environ['OSBOT_LAMBDA_S3_KEY_PREFIX'     ] = 'OSBOT_LAMBDA_S3_KEY_PREFIX'
        os.environ['OSBOT_LAMBDA_LAYERS_S3_BUCKET'  ] = 'OSBOT_LAMBDA_LAYERS_S3_BUCKET'
        os.environ['OSBOT_LAMBDA_ROLE_NAME'         ] = 'OSBOT_LAMBDA_ROLE_NAME'
        os.environ['OSBOT_NAME'                     ] = 'OSBOT_NAME'

        from osbot_aws.Globals import Globals
        assert Globals.aws_session_profile_name     == 'AWS_PROFILE_NAME'
        assert Globals.aws_session_region_name      == 'AWS_REGION_NAME'
        assert Globals.aws_session_account_id       == 'AWS_ACCOUNT_ID'
        assert Globals.lambda_s3_bucket             == 'OSBOT_LAMBDA_S3_BUCKET'
        assert Globals.lambda_s3_key_prefix         == 'OSBOT_LAMBDA_S3_KEY_PREFIX'
        assert Globals.lambda_layers_s3_bucket      == 'OSBOT_LAMBDA_LAYERS_S3_BUCKET'
        assert Globals.lambda_role_name             == 'OSBOT_LAMBDA_ROLE_NAME'
        assert Globals.bot_name                     == 'OSBOT_NAME'