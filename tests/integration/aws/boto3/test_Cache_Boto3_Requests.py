import pytest
from os                                                                 import environ
from unittest                                                           import TestCase
from botocore.client                                                    import BaseClient
from osbot_utils.utils.Env                                              import load_dotenv
from osbot_aws.aws.boto3.Cache_Boto3_Requests                           import Cache_Boto3_Requests, SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE, SQLITE_TABLE_NAME__BOTO3_REQUESTS
from osbot_aws.aws.sts.STS                                              import STS
from osbot_utils.base_classes.Kwargs_To_Self                            import Kwargs_To_Self
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests           import Sqlite__Cache__Requests
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests__Patch    import Sqlite__Cache__Requests__Patch
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Local               import ENV_NAME_PATH_LOCAL_DBS
from osbot_utils.utils.Files                                            import current_temp_folder, parent_folder, temp_file, file_extension, folder_exists
from osbot_utils.utils.Objects                                          import base_types


class test_Cache_Boto3_Requests(TestCase):
    cache_boto3_requests : Cache_Boto3_Requests
    temp_db_path         : str

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        cls.temp_db_path = temp_file(extension='sqlite')
        cls.cache_boto3_requests = Cache_Boto3_Requests(db_path=cls.temp_db_path)

    @classmethod
    def tearDownClass(cls):
        cls.cache_boto3_requests.delete()
        assert cls.cache_boto3_requests.sqlite_requests.exists() is False
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'        # confirm the original function is still there

    def test__init__(self):
        with self.cache_boto3_requests as _:

            # assert _.__attr_names__()                         == ['add_source_location', 'add_timestamp', 'cache_actions', 'cache_data',
            #                                                       'cache_only_mode', 'capture_exceptions', 'db_name','enabled',
            #                                                       'exception_classes', 'on_invoke_target', 'pickle_response', 'sqlite_requests',
            #                                                       'table_name','target_class', 'target_function', 'target_function_name','update_mode']
            assert _.db_name                                  == SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
            assert _.table_name                               == SQLITE_TABLE_NAME__BOTO3_REQUESTS
            assert _.sqlite_requests.exists()                 is True
            assert _.cache_entries()                          == []
            assert _.cache_table.new_row_obj().__locals__() == {'comments'        : ''    ,
                                                                'metadata'        : ''    ,
                                                                'request_data'    : ''    ,
                                                                'request_hash'    : ''    ,
                                                                'request_type'    : ''    ,
                                                                'response_bytes'  : b''   ,
                                                                'response_data'   : ''    ,
                                                                'response_hash'   : ''    ,
                                                                'response_type'   : ''    ,
                                                                'source'          : ''    ,
                                                                'timestamp'       : 0     }
            assert parent_folder (_.sqlite_requests.db_path)  == current_temp_folder()
            assert file_extension(_.sqlite_requests.db_path)  == '.sqlite'
            assert base_types(_)                              == [Sqlite__Cache__Requests__Patch ,
                                                                  Sqlite__Cache__Requests        ,
                                                                  Kwargs_To_Self                 ,
                                                                  object                         ]
            assert _.target_class                             == BaseClient
            assert _.target_function                          != BaseClient._make_api_call
            assert _.target_function_name                     == "_make_api_call"
        assert _.target_function == BaseClient._make_api_call

    def test___enter____exit__(self):
        assert BaseClient._make_api_call == BaseClient._make_api_call
        assert BaseClient._make_api_call == self.cache_boto3_requests.target_function
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'
        with self.cache_boto3_requests  as _:
            assert BaseClient._make_api_call              != self.cache_boto3_requests.target_function
            assert BaseClient._make_api_call.__qualname__ == 'Sqlite__Cache__Requests__Patch.patch_apply.<locals>.proxy'
        assert BaseClient._make_api_call == self.cache_boto3_requests.target_function
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'

    
    def test_invoke_target(self):
        mock_account_id = 'ABC'
        def on_invoke_target(*args):
            return {'Account': mock_account_id}

        with self.cache_boto3_requests as _:
            _.set__add_timestamp(False)
            _.set_on_invoke_target(on_invoke_target)

            assert _.cache_entries() == []

            sts         = STS()
            account_id  = sts.current_account_id()
            cache_entry = _.cache_entries()[0]

            assert mock_account_id        == account_id
            assert len(_.cache_entries()) == 1

            # assert cache_entry == { 'comments'      : ''            ,
            #                         'metadata'      : ''            ,
            #                         'id'            : 1             ,
            #                         'request_data'  : '"{\\n    \\"operation_name\\": '
            #                                            '\\"GetCallerIdentity\\",\\n    \\"api_params\\": {}\\n}"',
            #                         'request_hash'  : '612f59e11f66106d9aae85311816db22a1e78fce2825c76729ac35e66e76b76e',
            #                         'request_type'  : ''                                                ,
            #                         'response_bytes': b'\x80\x04\x95\x14\x00\x00\x00\x00\x00\x00\x00}'
            #                                           b'\x94\x8c\x07Account\x94\x8c\x03ABC\x94s.'       ,
            #                         'response_data' : ''            ,
            #                         'response_hash' : '518b16376e65e96e9ec8165b7e7d66054eceadafb8950b866f4839ece7711177'            ,
            #                         'response_type' : 'pickle'      ,
            #                         'source'        : ''            ,
            #                         'timestamp'     : 0             }

class test_Cache_Boto3_Requests__Local_DBs(TestCase):
    cache_boto3_requests: Cache_Boto3_Requests

    @classmethod
    def setUpClass(cls):
        load_dotenv()
        if not environ.get(ENV_NAME_PATH_LOCAL_DBS):
            pytest.skip("skipping tests because ENV_NAME_PATH_LOCAL_DBS var is not set")
        cls.cache_boto3_requests = Cache_Boto3_Requests()

    def test__init__(self):
        path_local_dbs = environ.get(ENV_NAME_PATH_LOCAL_DBS)
        assert folder_exists(path_local_dbs)
        with self.cache_boto3_requests as _:
            assert _.table_name                               == SQLITE_TABLE_NAME__BOTO3_REQUESTS
            assert _.db_name                                  == SQLITE_DB_NAME__BOTO3_REQUESTS_CACHE
            assert parent_folder (_.sqlite_requests.db_path)  == path_local_dbs
            assert file_extension(_.sqlite_requests.db_path)  == '.sqlite'
            assert _.sqlite_requests.exists()                 is True
            assert _.cache_table.exists()                   is True



