import random
import string

from osbot_utils.testing.Temp_Env_Vars import Temp_Env_Vars


class Temp__Random__AWS_Credentials(Temp_Env_Vars):

    def __init__(self, **kwargs):
        empty_aws_credentials = dict(                           # Create the AWS credentials with realistic random values
            AWS_ACCESS_KEY_ID       =   self.random_aws_access_key_id    (),
            AWS_SECRET_ACCESS_KEY   =   self.random_aws_secret_access_key(),
            AWS_ACCOUNT_ID          =   self.random_aws_account_id       (),
            AWS_DEFAULT_REGION      =   self.random_aws_region           ()
        )

        kwargs['env_vars'] = empty_aws_credentials
        super().__init__(**kwargs)

    # Helper functions to generate random values matching AWS schema

    def random_aws_access_key_id(self):
        return 'AKIA' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))       # AWS access key IDs are typically 20 characters long, uppercase letters and digits

    def random_aws_secret_access_key(self):
        return ''.join(random.choices(string.ascii_letters + string.digits + '/+=', k=40))          # AWS secret access keys are typically 40 characters long, mix of letters, digits, and special characters

    def random_aws_account_id(self):
        return ''.join(random.choices(string.digits, k=12))                                         # AWS account IDs are typically 12 digits long

    def random_aws_region(self):
        regions = [ 'us-east-1'     , 'us-west-1'   , 'us-west-2'     ,
                    'eu-west-1'     , 'eu-central-1', 'ap-southeast-1',
                    'ap-northeast-1', 'ap-south-1'  , 'sa-east-1'     ]
        return random.choice(regions)                                                               # Randomly select from a list of common AWS regions
