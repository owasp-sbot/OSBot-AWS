from osbot_utils.testing.Temp_Env_Vars import Temp_Env_Vars


class Temp__Empty__AWS_Credentials(Temp_Env_Vars):

    def __init__(self, **kwargs):
        empty_aws_credentials = dict(AWS_ACCESS_KEY_ID     = '',
                                     AWS_SECRET_ACCESS_KEY = '',
                                     AWS_ACCOUNT_ID        = '',
                                     AWS_DEFAULT_REGION    = '')
        kwargs['env_vars'] = empty_aws_credentials
        super().__init__(**kwargs)