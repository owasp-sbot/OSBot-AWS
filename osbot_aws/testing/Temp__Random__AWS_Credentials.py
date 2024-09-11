from osbot_utils.testing.Temp_Env_Vars import Temp_Env_Vars
from osbot_utils.utils.Misc import random_text


class Temp__Random__AWS_Credentials(Temp_Env_Vars):

    def __init__(self, **kwargs):
        empty_aws_credentials = dict(AWS_ACCESS_KEY_ID     = random_text(prefix='aws_access_key_id'    ),       # todo: see if we to have values that match the schema of these variables
                                     AWS_SECRET_ACCESS_KEY = random_text(prefix='aws_secret_access_key'),
                                     AWS_ACCOUNT_ID        = random_text(prefix='aws_account_id'       ),
                                     AWS_DEFAULT_REGION    = random_text(prefix='aws_default_region'   ))
        kwargs['env_vars'] = empty_aws_credentials
        super().__init__(**kwargs)