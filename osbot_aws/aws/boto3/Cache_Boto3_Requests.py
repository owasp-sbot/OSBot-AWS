from botocore.client                                                    import BaseClient
from botocore.exceptions                                                import ClientError
from osbot_utils.helpers.sqlite.domains.Sqlite__Cache__Requests__Patch  import Sqlite__Cache__Requests__Patch
from osbot_utils.utils.Yaml                                             import yaml_to_str

SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE = 'boto3_requests_cache.sqlite'
SQLITE_TABLE_NAME__BOTO3_REQUESTS    = 'boto3_requests'

class Cache_Boto3_Requests(Sqlite__Cache__Requests__Patch):

    def __init__(self, db_path=None):
        self.target_class           = BaseClient
        self.target_function        = BaseClient._make_api_call
        self.target_function_name   = "_make_api_call"
        self.db_name                = SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
        self.table_name             = SQLITE_TABLE_NAME__BOTO3_REQUESTS
        self.capture_exceptions     = True
        self.exception_classes      = [ClientError]
        #self.print_requests         = False
        super().__init__(db_path=db_path)

    def invoke_target(self, target, target_args, target_kwargs):
        #if self.print_requests:
            #print(f'[invoke_target]: {target_args}')
        return super().invoke_target(target, target_args, target_kwargs)

    def request_data(self, *args, **kwargs):
        target_self, operation_name, api_params = args
        request_data =  {'operation_name': operation_name,
                        'api_params'    : api_params    }
        #if self.print_requests:
            #print(f'[request_data]: {request_data}')
        request_data = yaml_to_str(request_data)
        return request_data