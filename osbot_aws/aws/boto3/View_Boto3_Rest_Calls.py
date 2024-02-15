from functools import wraps

from botocore.client                 import BaseClient

from osbot_utils.helpers.Print_Table import Print_Table
from osbot_utils.utils.Call_Stack import Call_Stack
from osbot_utils.utils.Dev import pformat

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
    print_call_stack    : bool        = True
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
        if self.config__print_calls:
            self.print_calls()
        return self.hook_method.__exit__(type=exception_type, value=exception_value,traceback=traceback)

    def print_data(self):
        total_duration  = round(self.total_duration.seconds(), 2)
        title           = f"BOTO3 REST calls (via BaseClient._make_api_call)"
        footer          = f"Total Duration: {total_duration:6} secs | Total calls: {len(self.hook_method.calls)} {' ':8}"
        #headers  = f"{'#':2} | {'Method':22} | {'Duration':7} | {'Params':42} | {'Return Value':42}"
        headers_data = { '#': 2, 'Method': 22, 'Duration': 7, 'Params': 42, 'Return Value': 42 }
        headers = " | ".join(f"{header:{width}}" for header, width in headers_data.items())
        rows_data = []
        for call in self.hook_method.calls:
            api_name     = call.get('args'  )[1]
            args         = call.get('args'  )[2:]
            call_stack   = call.get('call_stack')
            kwargs       = call.get('kwargs')           # see if this is relevant to any calls
            return_value = pformat(call.get('return_value'))
            duration     = call.get('duration')
            index        = call.get('index')
            if hasattr(return_value, 'ResponseMetadata'):
                del return_value['ResponseMetadata']
            row_data = dict(api_name     = api_name     ,
                            args         = args         ,
                            index        = index        ,
                            kwargs       = kwargs       ,
                            duration     = duration     ,
                            return_value = return_value )
            rows_data.append(row_data)
            if self.print_call_stack:
                call_stack.print()

        return { 'headers'      : headers       ,
                 'headers_data' : headers_data  ,
                 'footer'       : footer        ,
                 'rows_data'    : rows_data     ,
                 'title'        : title         }

    def print_calls(self):
        print_data = self.print_data()
        rows_data  = print_data.get('rows_data')
        with Print_Table() as _:
            _.set_title(print_data.get('title'))
            _.set_footer(print_data.get('footer'))
            _.add_data(rows_data)
            _.set_order('index', 'api_name', 'duration', 'args', 'kwargs', 'return_value')
            _.print()


    def map_data(self):
        pass