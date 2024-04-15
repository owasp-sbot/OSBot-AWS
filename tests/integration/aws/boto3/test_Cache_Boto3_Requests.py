from unittest import TestCase

from botocore.client import BaseClient

from osbot_aws.aws.boto3.Cache_Boto3_Requests import Cache_Boto3_Requests
from osbot_aws.aws.boto3.View_Boto3_Rest_Calls import print_boto3_calls
from osbot_aws.aws.iam.STS import STS
from osbot_utils.base_classes.Kwargs_To_Self import Kwargs_To_Self
from osbot_utils.helpers.sqlite.domains.Sqlite__Cache__Requests import Sqlite__Cache__Requests
from osbot_utils.helpers.sqlite.domains.Sqlite__Cache__Requests__Patch import Sqlite__Cache__Requests__Patch
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import current_temp_folder, parent_folder, file_name
from osbot_utils.utils.Objects import base_types


class test_Cache_Boto3_Requests(TestCase):
    cache_boto3_requests : Cache_Boto3_Requests

    @classmethod
    def setUpClass(cls):
        cls.cache_boto3_requests = Cache_Boto3_Requests()

    @classmethod
    def tearDownClass(cls):
        cls.cache_boto3_requests.delete()
        assert cls.cache_boto3_requests.sqlite_requests.exists() is False

    def test__init__(self):
        _ = self.cache_boto3_requests           # we can't use the with context here since it auto applies the patch

        assert _.__attr_names__() == ['add_timestamp', 'cache_only_mode', 'db_name','enabled','on_invoke_target',
                                      'pickle_response', 'sqlite_requests','table_name','target_class',
                                      'target_function', 'target_function_name','update_mode']
        assert _.db_name   .startswith('requests_cache_')
        assert _.table_name.startswith('requests_table_')
        assert _.sqlite_requests.exists() is True
        assert _.cache_entries() == []
        assert _.cache_table().new_row_obj().__locals__() == {'cache_hits'      : 0     ,
                                                              'comments'        : ''    ,
                                                              'latest'          : False ,
                                                              'request_data'    : ''    ,
                                                              'request_hash'    : ''    ,
                                                              'response_bytes'  : b''   ,
                                                              'response_data'   : ''    ,
                                                              'response_hash'   : ''    ,
                                                              'timestamp'       : 0     }
        assert parent_folder(_.sqlite_requests.db_path) == current_temp_folder()
        assert file_name    (_.sqlite_requests.db_path).startswith('requests_cache_')
        assert base_types(_) == [Sqlite__Cache__Requests__Patch ,
                                 Sqlite__Cache__Requests        ,
                                 Kwargs_To_Self                 ,
                                 object                         ]
        assert _.target_class           == BaseClient
        assert _.target_function        == BaseClient._make_api_call
        assert _.target_function_name   == "_make_api_call"

    def test___enter____exit__(self):
        assert BaseClient._make_api_call == BaseClient._make_api_call
        assert BaseClient._make_api_call == self.cache_boto3_requests.target_function
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'
        with self.cache_boto3_requests  as _:
            assert BaseClient._make_api_call              != self.cache_boto3_requests.target_function
            assert BaseClient._make_api_call.__qualname__ == 'Sqlite__Cache__Requests__Patch.patch_apply.<locals>.proxy'
        assert BaseClient._make_api_call == self.cache_boto3_requests.target_function
        assert BaseClient._make_api_call.__qualname__ == 'BaseClient._make_api_call'

    @print_boto3_calls()
    def test_invoke_target(self):
        mock_account_id = 'ABC'
        def on_invoke_target(*args):
            return {'Account': mock_account_id}

        with self.cache_boto3_requests as _:
            _.add_timestamp     = False
            _.on_invoke_target = on_invoke_target

            assert _.cache_entries() == []

            sts         = STS()
            account_id  = sts.current_account_id()
            cache_entry = _.cache_entries()[0]

            assert mock_account_id        == account_id
            assert len(_.cache_entries()) == 1

            assert cache_entry == { 'cache_hits'    : 0             ,
                                    'comments'      : ''            ,
                                    'id'            : 1             ,
                                    'latest'        : 0             ,
                                    'request_data'  : '"api_params: {}\\noperation_name: GetCallerIdentity\\n"',
                                    'request_hash'  : '2601fc898fb72b1f7b3207185225199a2f7370bb532f0e5448335c97ca319b85',
                                    'response_bytes': b'\x80\x04\x95\x14\x00\x00\x00\x00\x00\x00\x00}'
                                                      b'\x94\x8c\x07Account\x94\x8c\x03ABC\x94s.',
                                    'response_data' : ''            ,
                                    'response_hash' : ''            ,
                                    'timestamp'     : 0             }

    @print_boto3_calls()
    def test__make_boto3_call(self):
        sts = STS()
        sts.current_account_id()

