from functools import wraps

from osbot_aws.aws.sts.STS import STS


class aws_inject:

    """injects a number of AWS Specific values"""
    def __init__(self, fields):
        self.fields = fields                                        # field to inject

    def __call__(self, function):
        @wraps(function)                                            # makes __name__ work ok
        def wrapper(*args,**kwargs):                                # wrapper function
            for field in self.fields.split(','):                    # split value provided by comma
                if field == 'region'    : kwargs[field] = STS().current_region_name()
                if field == 'account_id': kwargs[field] = STS().current_account_id()
            return function(*args,**kwargs)
        return wrapper