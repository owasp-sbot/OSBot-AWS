import os
from unittest import TestCase
from osbot_aws.Globals import Globals

class test_Globals(TestCase):

    def test_static_values(self):
        assert Globals.aws_session_profile_name == 'gw-bot'
        assert Globals.aws_session_region_name  == 'eu-west-1'
        assert Globals.aws_session_account_id   == '311800962295'
        assert Globals.bot_name                 == 'gw_bot'
        assert Globals.lambda_s3_bucket         == 'gw-bot-lambdas'
        assert Globals.lambda_s3_key_prefix     == 'lambdas'
        assert Globals.lambda_role_name         == 'gwbot-lambdas-temp'

    def test_environment_variables(self):
        assert Globals.aws_session_profile_name     == Globals.default_values['AWS_PROFILE_NAME'          ]
        assert Globals.aws_session_region_name      == Globals.default_values['AWS_REGION_NAME'           ]
        assert Globals.aws_session_account_id       == Globals.default_values['AWS_ACCOUNT_ID'            ]
        assert Globals.lambda_s3_bucket             == Globals.default_values['OSBOT_LAMBDA_S3_BUCKET'    ]
        assert Globals.lambda_s3_key_prefix         == Globals.default_values['OSBOT_LAMBDA_S3_KEY_PREFIX']
        assert Globals.lambda_role_name             == Globals.default_values['OSBOT_LAMBDA_ROLE_NAME'    ]
        assert Globals.bot_name                     == Globals.default_values['OSBOT_NAME'                ]