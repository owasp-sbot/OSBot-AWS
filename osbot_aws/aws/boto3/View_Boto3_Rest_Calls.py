from functools import wraps

from botocore.client                 import BaseClient
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self

from osbot_utils.testing.Duration import Duration
from osbot_utils.testing.Hook_Method import Hook_Method

# todo: create unit tests specifically for this class
# decorator
def print_boto3_calls(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        with View_Boto3_Rest_Calls():
            return function(*args, **kwargs)
    return wrapper


class View_Boto3_Rest_Calls(Kwargs_To_Self):
    config__print_calls : bool        = True
    target_module                     = BaseClient
    target_method       : str         = "_make_api_call"
    hook_method                       = None
    total_duration      : Duration

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_duration.print_result = False


    def __enter__(self):
        self.hook_method = Hook_Method(target_module=self.target_module, target_method=self.target_method)
        self.total_duration.start()
        return self.hook_method.__enter__()

    def __exit__(self, exception_type, exception_value, traceback):
        self.total_duration.end()
        self.print_calls()
        return self.hook_method.__exit__(type=exception_type, value=exception_value,traceback=traceback)

    def print_calls(self):
        if self.config__print_calls:
            total_duration = round(self.total_duration.seconds(),2)
            print()
            print()
            print(f"|-------------------------------------------------------------------------------------|")
            print(f"| BOTO3 REST calls (via BaseClient._make_api_call)                                    |")
            print(f"|-------------------------------------------------------------------------------------|")
            print(f"| {'#':2} | {'Method':22} | {'Duration':7} | {'Params':42} | {'Return Value':42} |")
            print(f"|-------------------------------------------------------------------------------------|")
            for call in self.hook_method.calls:
                api_name     = call.get('args'  )[1]
                args         = call.get('args'  )[1:]
                kwargs       = call.get('kwargs')           # see if this is relevant to any calls
                return_value = call.get('return_value')
                duration     = call.get('duration')
                index        = call.get('index')
                if hasattr(return_value, 'ResponseMetadata'):
                    del return_value['ResponseMetadata']
                print(f"| {index:2} | {api_name:22} | {duration:5} ms | {args} | {return_value}     |")
            print(f"|-------------------------------------------------------------------------------------|")
            print(f"| Total Duration: {total_duration:6} secs | Total calls: {len(self.hook_method.calls)} {' ':8} |")
            print(f"|-------------------------------------------------------------------------------------|")

