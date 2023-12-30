from functools import wraps

from botocore.client                 import BaseClient

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

class View_Boto3_Rest_Calls:
    def __init__(self, on_exit_print_calls=True):
        self.target_module       = BaseClient
        self.target_method       = "_make_api_call"
        self.hook_method         = None
        self.on_exit_print_calls = on_exit_print_calls
        self.total_duration      = Duration(print_result=False)

    def __enter__(self):
        self.hook_method = Hook_Method(target_module=self.target_module, target_method=self.target_method)
        self.total_duration.start()
        return self.hook_method.__enter__()

    def __exit__(self, exception_type, exception_value, traceback):
        self.total_duration.end()
        self.print_calls()
        return self.hook_method.__exit__(type=exception_type, value=exception_value,traceback=traceback)

    def print_calls(self):
        if self.on_exit_print_calls:
            total_duration = round(self.total_duration.seconds(),2)
            print()
            print()
            print(f"|-------------------------------------------------------|")
            print(f"| BOTO3 REST calls (via BaseClient._make_api_call)      |")
            print(f"|-------------------------------------------------------|")
            print(f"| {'#':2} | {'Method':22} | {'Duration':7} | {'Return Value':10} |")
            print(f"|-------------------------------------------------------|")
            for call in self.hook_method.calls:
                api_name     = call.get('args')[1]
                return_value = call.get('return_value')
                duration     = call.get('duration')
                index        = call.get('index')
                del return_value['ResponseMetadata']
                print(f"| {index:2} | {api_name:22} | {duration:5} ms | {return_value}     |")
            print(f"|-------------------------------------------------------|")
            print(f"| Total Duration: {total_duration:6} secs | Total calls: {len(self.hook_method.calls)} {' ':8} |")
            print(f"|-------------------------------------------------------|")

