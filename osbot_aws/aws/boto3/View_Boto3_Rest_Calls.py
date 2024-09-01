from functools                                  import wraps
from botocore.client                            import BaseClient
from osbot_utils.helpers.Print_Table            import Print_Table
from osbot_utils.utils.Dev                      import pformat
from osbot_utils.base_classes.Kwargs_To_Self    import Kwargs_To_Self
from osbot_utils.testing.Duration               import Duration
from osbot_utils.testing.Hook_Method            import Hook_Method
from osbot_utils.utils.Objects                  import obj_data


# todo: create unit tests specifically for this class
# decorator

# todo refactor ctor of print_boto3_calls to make these options available (and easier to use)
# config__print_args          : bool = True
# config__print_calls         : bool = True
# config__print_call_stack    : bool = False
# config__print_return_value  : bool = True
# config__print_pformat_args  : bool = True
# see above the multipe options that can be set via the decorator

def print_boto3_calls(show=True, show_args=True, show_calls= False, show_return=True, **decorator_kwargs):
    decorator_kwargs['config__print_args'        ] = show_args
    decorator_kwargs['config__print_call_stack'  ] = show_calls
    decorator_kwargs['config__print_calls'       ] = show
    decorator_kwargs['config__print_return_value'] = show_return
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            with View_Boto3_Rest_Calls(**decorator_kwargs):         # Pass decorator_kwargs to the View_Boto3_Rest_Calls class
                return function(*args, **kwargs)
        return wrapper
    return decorator


class View_Boto3_Rest_Calls(Kwargs_To_Self):
    config__print_args          : bool = True
    config__print_calls         : bool = True
    config__print_call_stack    : bool = False
    config__print_return_value  : bool = True                       # todo: add better support for this (for example not showing the column if this is False)
    config__print_pformat_args  : bool = True
    target_module                      = BaseClient
    target_method               : str  = "_make_api_call"
    hook_method                        = None
    total_duration              : Duration

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
            duration     = call.get('duration')
            exception    = call.get('exception')
            index        = call.get('index')
            return_value = call.get('return_value')
            if return_value and 'ResponseMetadata' in return_value:
                del return_value['ResponseMetadata']
            if exception:
                # exception_data = obj_data(exception, name_width=100, value_width=1000)
                # return_value_str = pformat(exception_data)
                return_value_str = pformat(exception.args)
            else:
                if self.config__print_return_value:
                    return_value_str = pformat(return_value)
                else:
                    return_value_str = '(hidden)'

            if self.config__print_args is False:
                args = '(hidden)'
            if self.config__print_pformat_args:
                args= pformat(args)

            row_data = dict(api_name     = api_name         ,
                            args         = args             ,
                            index        = index            ,
                            kwargs       = kwargs           ,
                            duration     = duration         ,
                            return_value = return_value_str )
            rows_data.append(row_data)
            if self.config__print_call_stack:               # todo: this needs improvement since at the momment the call stacks are show at the top of the console logs
                call_stack.print()

        return { 'headers'      : headers       ,
                 'headers_data' : headers_data  ,
                 'footer'       : footer        ,
                 'rows_data'    : rows_data     ,
                 'title'        : title         }

    def print_calls(self):
        print_data = self.print_data()
        rows_data  = print_data.get('rows_data')
        if rows_data:
            order = ['index', 'api_name', 'duration', 'args', 'kwargs', 'return_value']
        else:
            order = []
        with Print_Table() as _:
            _.set_title(print_data.get('title'))
            _.set_footer(print_data.get('footer'))
            _.add_data(rows_data)
            _.set_order(*order)
            _.print()


    def map_data(self):
        pass