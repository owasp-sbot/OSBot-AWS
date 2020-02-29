from functools import wraps

# todo: create signature based on request params so that we don't cache when the params are different
from osbot_aws.Globals import Globals


def cache(function):
    @wraps(function)
    def wrapper(*args,**kwargs):
        if hasattr(function, 'return_value') is False:                  # check if return_value has been set
            function.return_value  = function(*args,**kwargs)           # invoke function and capture the return value
        return function.return_value                                    # return the return value
    return wrapper


def catch(function):
    """Catches any errors and returns an object with the error"""
    @wraps(function)                                                    # so that when we call the __name__ of the called we get the correct name (for example self.aws_lambda.alias.__name__)
    def wrapper(*args,**kwargs):
        try:
            return function(*args,**kwargs)
        except Exception as error:
            return {'error': error }
    return wrapper

class aws_inject:
    """injects a number of AWS Specific values"""
    def __init__(self, fields):
        self.fields = fields                                        # field to inject

    def __call__(self, function):
        @wraps(function)                                            # makes __name__ work ok
        def wrapper(*args,**kwargs):                                # wrapper function
            for field in self.fields.split(','):                    # split value provided by comma
                if field == 'region'    : kwargs[field] = Globals.aws_session_region_name
                if field == 'account_id': kwargs[field] = Globals.aws_session_account_id
            return function(*args,**kwargs)
        return wrapper                                              # return wrapper function


class remove:
    """removes the field from the return value of the function (if it exists"""
    def __init__(self, field_name):
        self.field_name = field_name                                # field to remove

    def __call__(self, function):
        @wraps(function)                                            # makes __name__ work ok
        def wrapper(*args,**kwargs):                                # wrapper function
            data = function(*args,**kwargs)                         # calls wrapped function with original params
            if data and data.get(self.field_name) is not None:      # check if field_name exists in data
                del data[self.field_name]                           # if it does, delete it
            return data                                             # return data received
        return wrapper                                              # return wrapper function

