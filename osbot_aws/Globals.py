import os

# Globals vars

class Globals:
    """
    These settings are used in many classes
    If you want to override them, just export the ENV var with the correspondent name.
    """
    aws_session_profile_name = os.getenv('AWS_PROFILE', 'default')
    aws_session_region_name  = os.getenv('AWS_REGION_NAME', 'eu-west-2')
    lambda_s3_bucket         = os.getenv('OSBOT_LAMBDA_BUCKET', 'gs-lambda-tests')
    aws_userid               = os.getenv('OSBOT_AWS_USERID', '244560807427')