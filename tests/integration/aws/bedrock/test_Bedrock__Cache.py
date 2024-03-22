import sqlite3
from unittest import TestCase

from osbot_aws.aws.bedrock.cache.Bedrock__Cache import Bedrock__Cache
from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock import PATH_FILE__SQLITE_BEDROCK
from osbot_aws.aws.bedrock.cache.Sqlite__Bedrock__Row import Sqlite__Bedrock__Row, Sqlite__Bedrock__Row__Type
from osbot_utils.helpers.sqlite.Sqlite__Cursor import Sqlite__Cursor
from osbot_utils.utils.Dev import pprint
from osbot_utils.utils.Misc import random_string, str_sha256


class test_Bedrock__Cache(TestCase):

    def setUp(self):
        self.bedrock_cache = Bedrock__Cache()

    # @trace_calls(ignore         = []    , include        = ['osbot_'], contains=[]                 ,
    #              source_code    = False , show_lines     = False ,
    #              show_duration  = True , duration_bigger_than = 0.001,
    #              show_class     = True , show_locals    = False ,
    #              show_types     = False  , show_internals = True , extra_data = False          ,
    #              show_types_padding = 100  , duration_padding=120,
    #              enabled        = False  )

    def test_cache_add(self):
        #self.bedrock_cache.sqlite_bedrock.table_requests__reset()
        request_type     = Sqlite__Bedrock__Row__Type.UNIT_TEST
        request_data     = {'the':'request_data', 'random_value' : random_string()}
        response_data    = {'the':'response_data'}

        new_row_req_hash = '91206458cc372081ebbe74ad8722b24c94c426d079629d888d62089e10e3980a'

        with self.bedrock_cache.cache_table() as _:
           _.select_rows_where(request_hash=new_row_req_hash)
        return
        new_row          = self.bedrock_cache.cache_add(request_data, response_data,request_type)
        new_row_req_hash = new_row.request_hash
        pprint(new_row_req_hash)
        with self.bedrock_cache.cache_table() as _:
           _.print()
        pprint(new_row)

    def test_setup(self):
        with self.bedrock_cache.sqlite_bedrock as _:
            assert _.db_path == PATH_FILE__SQLITE_BEDROCK

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

