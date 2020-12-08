import os

from dotenv import load_dotenv


class AWS_Config:

    def __init__(self):
        load_dotenv()

    def aws_session_profile_name(self): return os.getenv('AWS_PROFILE_NAME'          )
    def aws_session_region_name (self): return os.getenv('AWS_DEFAULT_REGION'        )
    def aws_session_account_id  (self): return os.getenv('AWS_ACCOUNT_ID'            )
    def lambda_s3_bucket        (self): return os.getenv('OSBOT_LAMBDA_S3_BUCKET'    )
    def lambda_s3_key_prefix    (self): return os.getenv('OSBOT_LAMBDA_S3_KEY_PREFIX')
    def lambda_role_name        (self): return os.getenv('OSBOT_LAMBDA_ROLE_NAME'    )
    def bot_name                (self): return os.getenv('OSBOT_NAME'                )