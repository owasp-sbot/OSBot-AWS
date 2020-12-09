import os

from dotenv import load_dotenv


class AWS_Config:

    def __init__(self):
        load_dotenv()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def aws_session_profile_name(self): return os.getenv('AWS_PROFILE_NAME'          )
    def aws_session_region_name (self): return os.getenv('AWS_DEFAULT_REGION'        )
    def aws_session_account_id  (self): return os.getenv('AWS_ACCOUNT_ID'            )
    def lambda_s3_bucket        (self): return os.getenv('OSBOT_LAMBDA_S3_BUCKET'    )
    def lambda_s3_key_prefix    (self): return os.getenv('OSBOT_LAMBDA_S3_KEY_PREFIX')
    def lambda_role_name        (self): return os.getenv('OSBOT_LAMBDA_ROLE_NAME'    )
    def bot_name                (self): return os.getenv('OSBOT_NAME'                )


    def set_aws_session_profile_name(self, value): os.environ['AWS_PROFILE_NAME'          ] = value ; return value
    def set_aws_session_region_name (self, value): os.environ['AWS_DEFAULT_REGION'        ] = value ; return value
    def set_aws_session_account_id  (self, value): os.environ['AWS_ACCOUNT_ID'            ] = value ; return value
    def set_lambda_s3_bucket        (self, value): os.environ['OSBOT_LAMBDA_S3_BUCKET'    ] = value ; return value
    def set_lambda_s3_key_prefix    (self, value): os.environ['OSBOT_LAMBDA_S3_KEY_PREFIX'] = value ; return value
    def set_lambda_role_name        (self, value): os.environ['OSBOT_LAMBDA_ROLE_NAME'    ] = value ; return value
    def set_bot_name                (self, value): os.environ['OSBOT_NAME'                ] = value ; return value