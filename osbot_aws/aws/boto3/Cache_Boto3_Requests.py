import types

from botocore.client import BaseClient

from osbot_utils.helpers.sqlite.domains.Sqlite__Cache__Requests__Patch import Sqlite__Cache__Requests__Patch
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Yaml import yaml_parse, yaml_to_str

SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE = 'boto3_requests_cache.sqlite'

class Cache_Boto3_Requests(Sqlite__Cache__Requests__Patch):

    def __init__(self, db_path=None):
        self.target_class           = BaseClient
        self.target_function        = BaseClient._make_api_call
        self.target_function_name   = "_make_api_call"
        self.db_name                = SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
        super().__init__(db_path=db_path)

    def invoke_target(self, target, target_args, target_kwargs):
        #cached_response = {'Account': '470426667096'}
        #return cached_response
        return super().invoke_target(target, target_args, target_kwargs)

    def request_data(self, *args, **kwargs):
        target_self, operation_name, api_params = args
        request_data =  {'operation_name': operation_name,
                        'api_params'    : api_params    }

        request_data = yaml_to_str(request_data)
        return request_data