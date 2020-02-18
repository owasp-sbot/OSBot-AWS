# Globals vars

# these values must be set before running any OSBot-AWS commands
class Globals:
    aws_session_profile_name = 'gw-bot'             #'default'
    aws_session_region_name  = 'eu-west-1'          #'eu-west-2'
    aws_session_account_id   = '311800962295'       #'....'
    bot_name                 = 'gw_bot'
    lambda_s3_bucket         = 'gw-bot-lambdas'     # must be unique in AWS
    lambda_role_name         = 'gwbot-lambdas-temp'
    lambda_s3_key_prefix     = 'lambdas'