import os

# Globals vars

# these values must be set before running any OSBot-AWS commands
class Globals:
    aws_session_profile_name = os.getenv('AWS_PROFILE', 'gw-bot')        #'default'
    aws_session_region_name  = os.getenv('AWS_REGION_NAME','eu-west-1')  #'eu-west-2'
    lambda_layers_s3_bucket  = 'gw-proxy-lambda-layers' # must be unique in AWS
    aws_session_account_id   = os.getenv('OSBOT_AWS_USERID','311800962295')           #'....'
    bot_name                 = 'gw_bot'
    lambda_s3_bucket         = os.getenv('OSBOT_LAMBDA_BUCKET','gw-bot-lambdas')         # must be unique in AWS
    lambda_role_name         = 'gwbot-lambdas-temp'
    lambda_s3_key_prefix     = 'lambdas'

