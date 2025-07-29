import random
import string
from osbot_utils.utils.Env              import get_env
from osbot_utils.testing.Temp_Env_Vars  import Temp_Env_Vars

OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID     = '000000000000'               # default local-stack account id for lambdas
OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION = 'us-east-1'                  # default local-stack region for lambdas


class Temp__Random__AWS_Credentials(Temp_Env_Vars):
    AWS_ACCESS_KEY_ID     : str = None
    AWS_SECRET_ACCESS_KEY : str = None
    AWS_ACCOUNT_ID        : str = None
    AWS_DEFAULT_REGION    : str = None

    def __enter__(self):
        self.with_default_credentials()         # this will call the super().set_vars()
        return self


    def with_localstack_credentials(self):
        self.AWS_ACCOUNT_ID        = OSBOT_AWS__LOCAL_STACK__AWS_ACCOUNT_ID
        self.AWS_DEFAULT_REGION    = OSBOT_AWS__LOCAL_STACK__AWS_DEFAULT_REGION
        self.AWS_ACCESS_KEY_ID     = self.random_aws_access_key_id()
        self.AWS_SECRET_ACCESS_KEY = self.random_aws_secret_access_key()
        self.set_aws_env_vars()
        return self

    def with_default_credentials(self):         # Set default credentials, using existing values or generating new ones.
        if not self.AWS_ACCESS_KEY_ID    : self.AWS_ACCESS_KEY_ID     = get_env('AWS_ACCESS_KEY_ID'    ) or self.random_aws_access_key_id    ()       # Generate new values only if not already set
        if not self.AWS_SECRET_ACCESS_KEY: self.AWS_SECRET_ACCESS_KEY = get_env('AWS_SECRET_ACCESS_KEY') or self.random_aws_secret_access_key()
        if not self.AWS_ACCOUNT_ID       : self.AWS_ACCOUNT_ID        = get_env('AWS_ACCOUNT_ID'       ) or self.random_aws_account_id       ()
        if not self.AWS_DEFAULT_REGION   : self.AWS_DEFAULT_REGION    = get_env('AWS_DEFAULT_REGION'   ) or self.random_aws_region           ()

        self.set_aws_env_vars()
        return self

    def set_aws_env_vars(self):                         # Update env_vars with the credentials
        aws_credentials = { 'AWS_ACCESS_KEY_ID'     : self.AWS_ACCESS_KEY_ID    ,
                            'AWS_SECRET_ACCESS_KEY' : self.AWS_SECRET_ACCESS_KEY,
                            'AWS_ACCOUNT_ID'        : self.AWS_ACCOUNT_ID       ,
                            'AWS_DEFAULT_REGION'    : self.AWS_DEFAULT_REGION   }
        self.env_vars.update(aws_credentials)
        self.set_vars()
        return self

    def random_aws_access_key_id(self):
        return 'AKIA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))       # AWS access key IDs are typically 20 characters long, uppercase letters and digits

    def random_aws_secret_access_key(self):
        return ''.join(random.choices(string.ascii_letters + string.digits + '/+=', k=40))          # AWS secret access keys are typically 40 characters long, mix of letters, digits, and special characters

    def random_aws_account_id(self):
        return ''.join(random.choices(string.digits, k=12))                                         # AWS account IDs are typically 12 digits long

    def random_aws_region(self):
        regions = [ 'us-west-1'     , 'us-west-2'   ,                       # 'us-east-1' # note: not using us-east-1 since it was causing some side effects with Local_Stack bucket creation (InvalidLocationConstraint error)
                    'eu-west-1'     , 'eu-central-1', 'ap-southeast-1',
                    'ap-northeast-1', 'ap-south-1'  , 'sa-east-1'     ]
        return random.choice(regions)                                                               # Randomly select from a list of common AWS regions


Temp_AWS_Credentials = Temp__Random__AWS_Credentials