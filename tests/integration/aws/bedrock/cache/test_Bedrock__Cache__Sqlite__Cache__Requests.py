from unittest import TestCase
from unittest.mock import Mock

import pytest

from osbot_aws.aws.bedrock.cache.Bedrock__Cache                         import Bedrock__Cache
from osbot_utils.helpers.sqlite.cache.db.Sqlite__DB__Requests           import Sqlite__DB__Requests
from osbot_utils.helpers.sqlite.cache.db.Schema__Table__Requests        import Schema__Table__Requests
from osbot_utils.utils.Files                                            import temp_file, parent_folder, file_exists, current_temp_folder, file_not_exists
from osbot_utils.utils.Json                                             import json_dump, json_dumps, to_json_str, json_loads, from_json_str
from osbot_utils.utils.Misc                                             import random_text, random_string, str_sha256, list_set

class test_Bedrock__Cache__Sqlite__Cache__Requests(TestCase):

    bedrock_cache : Bedrock__Cache
    temp_db_path  : str

    @classmethod
    def setUpClass(cls):
        cls.temp_db_path                = temp_file(extension='sqlite')
        cls.bedrock_cache               = Bedrock__Cache(db_path = cls.temp_db_path)            # the db_path to the tmp file path
        cls.bedrock_cache.set__add_timestamp(False)                                                 # disabling timestamp since it complicates the test data verification below
        assert parent_folder(cls.bedrock_cache.sqlite_requests.db_path) == current_temp_folder()
        assert file_exists  (cls.temp_db_path)                         is True

    @classmethod
    def tearDownClass(cls):    #file_delete(cls.temp_db_path)
        cls.bedrock_cache.sqlite_requests.delete()
        assert file_not_exists(cls.temp_db_path) is True

    def tearDown(self):
        self.bedrock_cache.cache_table().clear()

    def add_test_request(self):
        bedrock       = Mock()
        model_id      = random_text('random_model')
        body          = {'the': random_text('random_request')}
        response_data = {'the': random_text('random_response')}
        kwargs        = dict(bedrock=bedrock, model_id=model_id, body=body)

        bedrock.model_invoke.return_value = response_data
        self.bedrock_cache.model_invoke(**kwargs)

    def test_cache_add(self):
        self.bedrock_cache.sqlite_requests.table_requests__reset()
        request_data         = {'the':'request_data', 'random_value' : random_string()}
        request_data_json    = json_dump(request_data)
        request_data_sha256  = str_sha256(request_data_json)
        response_data        = {'the':'response_data'}
        response_data_json   = json_dump(response_data)
        response_data_sha256 = str_sha256(response_data_json)
        expected_new_row     = { 'comments'       : ''                   ,
                                 'metadata'       : ''                   ,
                                 'request_data'   : request_data_json    ,
                                 'request_hash'   : request_data_sha256  ,
                                 'request_type'   : ''                   ,
                                 'response_bytes' : b''                  ,
                                 'response_data'  : response_data_json   ,
                                 'response_hash'  : response_data_sha256 ,
                                 'response_type'  : 'dict'               ,
                                 'source'         : ''                   ,
                                 'timestamp'      : 0                    }
        expected_row_entry   = { **expected_new_row                      ,
                                 'id'            : 1                     }

        new_row = self.bedrock_cache.cache_add(request_data, response_data)
        assert new_row.json() == expected_new_row

        with self.bedrock_cache.cache_table() as _:
            rows = _.select_rows_where(request_hash=request_data_sha256)
            assert len(rows) == 1
            row = rows [0]
            assert row == expected_row_entry

            assert self.bedrock_cache.cache_entry(request_data) == expected_row_entry   # confirm we can get the row via it's row_data
            _.rows_delete_where(request_hash=request_data_sha256)                       # delete added row
            assert _.rows() == []                                                       # confirm we are back to having an empty table
            assert self.bedrock_cache.cache_entry(request_data) == {}                   # confirm entry is not available anymore

    def test_cache_delete(self):
        request_data  = {'an': 'request' }
        response_data = {'an': 'response'}
        with self.bedrock_cache as _:
            row = _.cache_add(request_data, response_data)
            assert row.request_data         == to_json_str(request_data )
            assert row.response_data        == to_json_str(response_data)
            assert len (_.cache_entries())  == 1
            assert _.cache_delete(request_data).get('status') == 'ok'
            assert len(_.cache_entries())   == 0

    @pytest.mark.skip("Fix after refactoring of Sqlite__Cache__Requests has been completed")
    def test_cache_entry_comments(self):
        with self.bedrock_cache as _:
            assert _.cache_entries() == []
            model_id      = 'an_model'
            body          = {'answer': 42}
            new_comment   = random_string(prefix='new_comment')
            request_data  = {'model': model_id, 'body': body}
            response_data = {'in': 'response'}

            _.cache_add(request_data, response_data)

            cache_entry = _.cache_entries()[0]
            assert len(_.cache_entries()) == 1
            assert request_data          == json_loads(cache_entry.get('request_data'))
            assert response_data         == json_loads(cache_entry.get('response_data'))
            assert _.cache_entry_for_request_params(             model=model_id, body=body)               == cache_entry
            assert _.cache_entry_comments          (             model=model_id, body=body)               == ''
            assert _.cache_entry_comments_update   (new_comment, model=model_id, body=body).get('status') == 'ok'
            assert _.cache_entry_comments          (             model=model_id, body=body)                == new_comment
            assert _.cache_table__clear().get('status')  == 'ok'
            assert _.cache_entries()                     == []

    def test_create_new_cache_data(self):
        model_id                 = 'aaaa'
        body                     = {'the': 'request data'}
        response_data            = {'the': 'return value'}
        request_data             = self.bedrock_cache.cache_request_data(model_id, body)
        new_cache_entry          = self.bedrock_cache.create_new_cache_row_data(request_data, response_data)
        expected_new_cache_entry = {'request_data'  : json_dumps(request_data)                                           ,
                                    'request_hash'  : '1b16c63a54a704c20df7c449d04acb56f8c8d44a48e1d43bee20359536edcd71' ,
                                    'response_bytes': b''                                                                ,
                                    'response_data' : json_dumps(response_data)                                          ,
                                    'response_hash' : '69e330ec7bf6334aa41ecaf56797fa86345d3cf85da4c622821aa42d4bee1799' ,
                                    'response_type' : 'dict'                                                             ,
                                    'timestamp'     :  0                                                                 }
        expected_new_cache_obj   = { **expected_new_cache_entry,
                                     'comments'    : '' ,
                                     'metadata'    : '' ,
                                     'request_type': '' ,
                                     'source'      : '' ,
                                     'timestamp'   : 0  }
        assert new_cache_entry == expected_new_cache_entry
        new_cache_obj = self.bedrock_cache.cache_table().new_row_obj(new_cache_entry)
        assert new_cache_obj.__locals__() == expected_new_cache_obj
        assert self.bedrock_cache.cache_entries() ==[]

        self.bedrock_cache.set__add_timestamp(True)
        new_cache_entry = self.bedrock_cache.create_new_cache_row_data(request_data, response_data)
        assert new_cache_entry.get('timestamp') != 0
        assert new_cache_entry.get('timestamp') > 0
        self.bedrock_cache.set__add_timestamp(False)

    def test_disable(self):
        with self.bedrock_cache as _:
            assert _.config.enabled is True
            _.disable()
            assert _.config.enabled is False
            _.enable()
            assert _.config.enabled is True

    def test_only_from_cache(self):
        with self.bedrock_cache as _:
            assert _.config.cache_only_mode is False
            _.only_from_cache()
            assert _.config.cache_only_mode is True
            _.only_from_cache(False)
            assert _.config.cache_only_mode is False


    def test_requests_data__all(self):
        count = 2
        self.add_test_request()
        self.add_test_request()

        with self.bedrock_cache as _:
            for requests_data in _.requests_data__all():
                assert list_set(requests_data) == ['_comments','_hash', '_id', 'body', 'model']
            assert _.cache_table().size() == count

    def test_response_data_for__request_hash(self):
        assert self.bedrock_cache.response_data_for__request_hash('aaaa') == {}


    def test_setup(self):
        with self.bedrock_cache.sqlite_requests as _:
            assert type(_)   is Sqlite__DB__Requests
            assert _.db_path != Sqlite__DB__Requests().path_local_db()
            assert _.db_path == self.temp_db_path

        with self.bedrock_cache.cache_table() as _:

            _._table_create().add_fields_from_class(Schema__Table__Requests).sql_for__create_table()

            assert _.exists()   is True
            assert _.row_schema is Schema__Table__Requests
            assert _.schema__by_name_type() =={ 'comments'      : 'TEXT'    ,
                                                'id'            : 'INTEGER' ,
                                                'metadata'      : 'TEXT'    ,
                                                'request_data'  : 'TEXT'    ,
                                                'request_hash'  : 'TEXT'    ,
                                                'request_type'  : 'TEXT'    ,
                                                'response_bytes': 'BLOB'    ,
                                                'response_data' : 'TEXT'    ,
                                                'response_hash' : 'TEXT'    ,
                                                'response_type' : 'TEXT'    ,
                                                'source'        : 'TEXT'    ,
                                                'timestamp'     : 'INTEGER' }
            assert _.indexes() == ['idx__bedrock_requests__request_hash']


    def test_update(self):
        with self.bedrock_cache as _:
            assert _.config.update_mode is False
            _.update()
            assert _.config.update_mode is True
            _.update(False)
            assert _.config.update_mode is False