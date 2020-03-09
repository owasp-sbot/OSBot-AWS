import os

# Globals vars

# these values must be set before running any OSBot-AWS commands
# you can set them directly or via environment variables
class Globals:
    aws_session_profile_name = os.getenv('AWS_PROFILE_NAME'             , 'gw-bot'              ) # 'default'
    aws_session_region_name  = os.getenv('AWS_REGION_NAME'              , 'eu-west-1'           ) # 'eu-west-2'
    aws_session_account_id   = os.getenv('AWS_ACCOUNT_ID'               , '311800962295'        )
    lambda_s3_bucket         = os.getenv('OSBOT_LAMBDA_S3_BUCKET'       , 'gw-bot-lambdas'      ) # must be unique in AWS
    lambda_s3_key_prefix     = os.getenv('OSBOT_LAMBDA_S3_KEY_PREFIX'   , 'lambdas'             )
    lambda_layers_s3_bucket  = os.getenv('OSBOT_LAMBDA_LAYERS_S3_BUCKET', 'gw-bot-lambda-layers') # must be unique in AWS
    lambda_role_name         = os.getenv('OSBOT_LAMBDA_ROLE_NAME'       , 'gwbot-lambdas-temp'  )
    bot_name                 = os.getenv('OSBOT_NAME'                   , 'gw_bot'              )


