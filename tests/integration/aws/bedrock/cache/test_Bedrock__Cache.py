import sqlite3
from unittest import TestCase

from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock import PATH_FILE__SQLITE_BEDROCK
from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row, Sqlite__Bedrock__Row__Type
from osbot_utils.helpers.sqlite.Sqlite__Cursor import Sqlite__Cursor
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Files import temp_file, file_not_exists, file_delete, file_exists
from osbot_utils.utils.Json import json_dump
from osbot_utils.utils.Misc import random_string, str_sha256


class test_Bedrock__Cache(TestCase):
    bedrock_cache : Bedrock__Cache
    temp_db_path  : str

    @classmethod
    def setUpClass(cls):
        cls.temp_db_path  = temp_file(extension='sqlite')
        cls.bedrock_cache = Bedrock__Cache(db_path = cls.temp_db_path)          # the db_path to the tmp file path
        assert file_exists(cls.temp_db_path) is True

    @classmethod
    def tearDownClass(cls):    #file_delete(cls.temp_db_path)
        cls.bedrock_cache.sqlite_bedrock.delete()
        assert file_not_exists(cls.temp_db_path) is True



    # @trace_calls(ignore         = []    , include        = ['osbot_'], contains=[]                 ,
    #              source_code    = False , show_lines     = False ,
    #              show_duration  = True , duration_bigger_than = 0.001,
    #              show_class     = True , show_locals    = False ,
    #              show_types     = False  , show_internals = True , extra_data = False          ,
    #              show_types_padding = 100  , duration_padding=120,
    #              enabled        = False  )

    def test_cache_add(self):
        self.bedrock_cache.sqlite_bedrock.table_requests__reset()
        request_type         = Sqlite__Bedrock__Row__Type.UNIT_TEST
        request_data         = {'the':'request_data', 'random_value' : random_string()}
        request_data_json    = json_dump(request_data)
        request_data_sha256  = str_sha256(request_data_json)
        response_data        = {'the':'response_data'}
        response_data_json   = json_dump(response_data)
        response_data_sha256 = str_sha256(response_data_json)

        new_row = self.bedrock_cache.cache_add(request_data, response_data, request_type)
        assert new_row.json() == { 'cache_hits'     : 0                    ,
                                   'latest'         : False                ,
                                   'record_type'    : request_type         ,
                                   'request_data'   : request_data_json    ,
                                   'request_hash'   : request_data_sha256  ,
                                   'response_data'  : response_data_json   ,
                                   'response_hash'  : response_data_sha256 ,
                                   'timestamp'      : 0                    }

        with self.bedrock_cache.cache_table() as _:
            rows = _.select_rows_where(request_hash=request_data_sha256)
            assert len(rows) == 1
            row = rows [0]
            assert row == { 'cache_hits'    : 0                     ,
                            'id'            : 1                     ,
                            'latest'        : 0                     ,
                            'record_type'   : request_type          ,
                            'request_data'  : request_data_json     ,
                            'request_hash'  : request_data_sha256   ,
                            'response_data' : response_data_json    ,
                            'response_hash' : response_data_sha256  ,
                            'timestamp'     : 0                     }           # BUG: value not being set
            _.rows_delete_where(request_hash=request_data_sha256)               # delete added row
            assert _.rows() == []                                               # confirm we are back to having an empty table


    def test_setup(self):
        with self.bedrock_cache.sqlite_bedrock as _:
            assert _.db_path != PATH_FILE__SQLITE_BEDROCK
            assert _.db_path == self.temp_db_path

        with self.bedrock_cache.cache_table() as _:

            _._table_create().add_fields_from_class(Sqlite__Bedrock__Row).sql_for__create_table()

            assert _.exists() is True
            assert _.row_schema is Sqlite__Bedrock__Row
            assert _.schema__by_name_type() == { 'cache_hits'   : 'INTEGER' ,
                                                 'id'           : 'INTEGER' ,
                                                 'latest'       : 'BOOLEAN' ,
                                                 'record_type'  : 'TEXT'    ,
                                                 'request_data' : 'TEXT'    ,
                                                 'request_hash' : 'TEXT'    ,
                                                 'response_data': 'TEXT'    ,
                                                 'response_hash': 'TEXT'    ,
                                                 'timestamp'    : 'INTEGER' }
            assert _.indexes() == ['idx__bedrock_requests__request_hash']

