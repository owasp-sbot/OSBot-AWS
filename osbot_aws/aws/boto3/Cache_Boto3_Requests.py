from botocore.client                                                    import BaseClient
from botocore.exceptions                                                import ClientError
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests__Patch    import Sqlite__Cache__Requests__Patch
from osbot_utils.utils.Call_Stack import call_stack_frames_data
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Json                                             import json_to_str

SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE = 'boto3_requests_cache.sqlite'
SQLITE_TABLE_NAME__BOTO3_REQUESTS    = 'boto3_requests'

class Cache_Boto3_Requests(Sqlite__Cache__Requests__Patch):

    def __init__(self, db_path=None):
        self.target_class                      = BaseClient
        self.target_function                   = BaseClient._make_api_call
        self.target_function_name              = "_make_api_call"
        self.db_name                           = SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
        self.table_name                        = SQLITE_TABLE_NAME__BOTO3_REQUESTS
        super().__init__(db_path=db_path)
        self.config.capture_exceptions         = True
        self.config.exception_classes          = [ClientError]
        self.add_caller_signature_to_cache_key = True                   # todo: move this to the main OSBot_Utils code base
        #self.print_requests         = False


    def cache_entry_comments(self, model_id, body):
        return super().cache_entry_comments(model_id=model_id, body=body)

    def cache_entry_comments_update(self, model_id, body, new_comments):
        return super().cache_entry_comments_update(new_comments, model_id=model_id, body=body)

    def invoke_target(self, target, target_args, target_kwargs):
        #if self.print_requests:
            #print(f'[invoke_target]: {target_args}')
        return super().invoke_target(target, target_args, target_kwargs)

    def request_data(self, *args, **kwargs):
        target_self, operation_name, api_params = args
        request_data =  {'operation_name': operation_name,
                        'api_params'    : api_params    }

        # need this in cases where we have multiple requests to the same method in the same tests
        if self.add_caller_signature_to_cache_key:                                     # todo: move this to the main OSBot_Utils code base
            frames_depth   = 15                                                        # todo find a better way to get the code that is changing
            frames_capture = frames_depth
            caller_signature = ''
            frames              = call_stack_frames_data(frames_depth)                 # todo: refactor this to separate method
            for frame in frames[0:frames_capture]:
                caller_signature += f"{frame.get('name')}:{frame.get('lineno')} | "
            request_data['caller_signature'] = caller_signature                      # this adds support for different caches to the same method call (main limitation is that it is directly tied with the line numbers)

        request_data = json_to_str(request_data)            # todo: this used to use yaml, change to a better mode
        return request_data