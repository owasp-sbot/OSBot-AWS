import os

from osbot_utils.base_classes.Type_Safe import Type_Safe
from osbot_utils.utils.Env import load_dotenv

DEFAULT__AWS_DEFAULT_REGION = 'eu-west-1'

class AWS_Config(Type_Safe):

    def __init__(self):
        super().__init__()
        load_dotenv()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def aws_access_key_id           (self): return os.getenv('AWS_ACCESS_KEY_ID'              )
    def aws_secret_access_key       (self): return os.getenv('AWS_SECRET_ACCESS_KEY'          )
    def aws_session_profile_name    (self): return os.getenv('AWS_PROFILE_NAME'               )
    def aws_session_region_name     (self): return os.getenv('AWS_DEFAULT_REGION'             ) or DEFAULT__AWS_DEFAULT_REGION
    def aws_session_account_id      (self): return os.getenv('AWS_ACCOUNT_ID'                 ) or  self.sts__session_account_id()

    def dev_skip_aws_key_check      (self): return os.getenv('DEV_SKIP_AWS_KEY_CHECK'        , False              )     # use to not have the 500ms check that happens during this check
    def bot_name                    (self): return os.getenv('OSBOT_NAME'                                         )     # todo: refactor variable to osbot_name (need to check for side effects)
    def lambda_s3_folder_layers     (self): return os.getenv('OSBOT_LAMBDA_S3_FOLDER_LAYERS' , 'layers'           )     # todo: change these static values to DEFAULT_.... ones
    def lambda_s3_folder_lambdas    (self): return os.getenv('OSBOT_LAMBDA_S3_FOLDER_LAMBDAS', 'lambdas'          )
    def lambda_role_name            (self): return os.getenv('OSBOT_LAMBDA_ROLE_NAME'          'role-osbot-lambda')

    def set_aws_access_key_id       (self, value): os.environ['AWS_ACCESS_KEY_ID'               ] = value ; return value
    def set_aws_secret_access_key   (self, value): os.environ['AWS_SECRET_ACCESS_KEY'           ] = value ; return value
    def set_aws_session_profile_name(self, value): os.environ['AWS_PROFILE_NAME'                ] = value ; return value
    def set_aws_session_region_name (self, value): os.environ['AWS_DEFAULT_REGION'              ] = value ; return value
    def set_aws_session_account_id  (self, value): os.environ['AWS_ACCOUNT_ID'                  ] = value ; return value
    def set_lambda_s3_bucket        (self, value): os.environ['OSBOT_LAMBDA_S3_BUCKET'          ] = value ; return value
    def set_lambda_s3_folder_layers (self, value): os.environ['OSBOT_LAMBDA_S3_FOLDER_LAYERS'   ] = value ; return value
    def set_lambda_s3_folder_lambdas(self, value): os.environ['OSBOT_LAMBDA_S3_FOLDER_LAMBDAS'  ] = value ; return value
    def set_lambda_role_name        (self, value): os.environ['OSBOT_LAMBDA_ROLE_NAME'          ] = value ; return value
    def set_bot_name                (self, value): os.environ['OSBOT_NAME'                      ] = value ; return value

    def sts__session_account_id(self):                   # to handle when the AWS_ACCOUNT_ID is not set
        if self.aws_configured():
            from osbot_aws.aws.sts.STS import STS           #   the use of this method is not advised
            return STS().current_account_id()               #   since this is quite an expensive method

    def sts__caller_identity_user(self):
        if self.aws_configured():
            from osbot_aws.aws.sts.STS import STS           #
            return STS().caller_identity_user()                  #

    # helper methods
    def account_id (self):
        return self.aws_session_account_id()

    def aws_configured(self):           # todo: add support for when the AWS is configured in EC2's account
        if self.aws_access_key_id():
            if self.aws_secret_access_key():
                if self.aws_session_region_name():
                    return True
        return False

    def lambda_s3_bucket(self):
        return self.resolve_lambda_bucket_name()

    def region_name(self):
        return self.aws_session_region_name()

    def resolve_lambda_bucket_name(self):
        bucket_name = os.getenv('OSBOT_LAMBDA_S3_BUCKET')
        if bucket_name is None:
            bucket_name = f'{self.aws_session_account_id()}--osbot-lambdas--{self.region_name()}' # this is a needed breaking change
        return bucket_name

    def resolve_temp_data_bucket_name(self):
        bucket_name = os.getenv('OSBOT_TEMP_DATA_S3_BUCKET')
        if bucket_name is None:
            bucket_name = f'{self.aws_session_account_id()}--temp-data--{self.region_name()}'
        return bucket_name

    def set_region(self,region_name):
        self.set_aws_session_region_name(region_name)

    def temp_data_bucket(self):
        return self.resolve_temp_data_bucket_name()

def set_aws_region(region_name):
    AWS_Config().set_aws_session_region_name(region_name)

aws_config = AWS_Config()