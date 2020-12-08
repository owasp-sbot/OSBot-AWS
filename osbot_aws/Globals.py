import os
from osbot_aws.Config import Config

# Globals vars
# these values must be set before running any OSBot-AWS commands
# you can set them directly or via environment variables



class Globals:
    config = Config()

    default_values = {                                      # todo - refactor to better solution to store unit tests values (since these values shouldn't be hardcoded in the source code
        'AWS_PROFILE_NAME'          : 'gw-bot'            ,
        'AWS_REGION_NAME'           : 'eu-west-1'         ,
        'AWS_ACCOUNT_ID'            : '311800962295'      ,
        'OSBOT_LAMBDA_S3_BUCKET'    : 'gw-bot-lambdas'    ,
        'OSBOT_LAMBDA_S3_KEY_PREFIX': 'lambdas'           ,
        'OSBOT_LAMBDA_ROLE_NAME'    : 'gwbot-lambdas-temp',
        'OSBOT_NAME'                : 'gw_bot'
    }

    aws_session_profile_name = os.getenv('AWS_PROFILE_NAME'             , default_values['AWS_PROFILE_NAME'          ])
    aws_session_region_name  = os.getenv('AWS_REGION_NAME'              , default_values['AWS_REGION_NAME'           ])
    aws_session_account_id   = os.getenv('AWS_ACCOUNT_ID'               , default_values['AWS_ACCOUNT_ID'            ])
    lambda_s3_bucket         = os.getenv('OSBOT_LAMBDA_S3_BUCKET'       , default_values['OSBOT_LAMBDA_S3_BUCKET'    ]) # must be unique in AWS
    lambda_s3_key_prefix     = os.getenv('OSBOT_LAMBDA_S3_KEY_PREFIX'   , default_values['OSBOT_LAMBDA_S3_KEY_PREFIX'])
    lambda_role_name         = os.getenv('OSBOT_LAMBDA_ROLE_NAME'       , default_values['OSBOT_LAMBDA_ROLE_NAME'    ])
    bot_name                 = os.getenv('OSBOT_NAME'                   , default_values['OSBOT_NAME'                ])


