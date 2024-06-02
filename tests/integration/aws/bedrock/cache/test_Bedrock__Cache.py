from os import environ
from unittest                                                           import TestCase
from unittest.mock                                                      import Mock

import pytest

from osbot_aws.aws.bedrock.cache.Bedrock__Cache                         import Bedrock__Cache, ENV_NAME_BEDROCK_DB_NAME, \
    SQLITE_DB_NAME__SQLITE_BEDROCK, SQLITE_TABLE__BEDROCK_REQUESTS
from osbot_utils.base_classes.Kwargs_To_Self                            import Kwargs_To_Self
from osbot_utils.helpers.sqlite.Sqlite__Database                        import Sqlite__Database
from osbot_utils.helpers.sqlite.cache.Sqlite__Cache__Requests           import Sqlite__Cache__Requests
from osbot_utils.helpers.sqlite.domains.Sqlite__DB__Local               import Sqlite__DB__Local
from osbot_utils.helpers.sqlite.cache.db.Sqlite__DB__Requests           import Sqlite__DB__Requests
from osbot_utils.testing.Stdout                                         import Stdout
from osbot_utils.utils.Files                                            import temp_file, file_not_exists, file_exists, parent_folder, current_temp_folder
from osbot_utils.utils.Json                                             import from_json_str
from osbot_utils.utils.Misc                                             import random_text, list_set
from osbot_utils.utils.Objects                                          import base_types


class test_Bedrock__Cache(TestCase):
    bedrock_cache : Bedrock__Cache
    temp_db_path  : str

    @classmethod
    def setUpClass(cls):
        cls.temp_db_path                = temp_file(extension='sqlite')
        cls.bedrock_cache               = Bedrock__Cache(db_path = cls.temp_db_path)              # the db_path to the tmp file path
        cls.bedrock_cache.set__add_timestamp(False)                                               # disabling timestamp since it complicates the test data verification below
        assert parent_folder(cls.bedrock_cache.sqlite_requests.db_path) == current_temp_folder()
        assert file_exists  (cls.temp_db_path)                         is True

    @classmethod
    def tearDownClass(cls):    #file_delete(cls.temp_db_path)
        cls.bedrock_cache.sqlite_requests.delete()
        assert file_not_exists(cls.temp_db_path) is True

    def tearDown(self):
        self.bedrock_cache.cache_table.clear()

    def test___init__(self):
        with self.bedrock_cache as _:
            assert type      (_)                is Bedrock__Cache
            assert base_types(_)                == [Sqlite__Cache__Requests, Kwargs_To_Self, object]
            assert _.db_name                    == environ.get(ENV_NAME_BEDROCK_DB_NAME) or SQLITE_DB_NAME__SQLITE_BEDROCK
            assert _.table_name                 == SQLITE_TABLE__BEDROCK_REQUESTS
            assert type      (_.sqlite_requests) is Sqlite__DB__Requests
            assert base_types(_.sqlite_requests) == [Sqlite__DB__Local, Sqlite__Database, Kwargs_To_Self, object]
            assert _.sqlite_requests.db_name     == _.db_name
            assert _.sqlite_requests.table_name  == _.table_name


    def add_test_requests(self, count=10):
        for i in range(count):
            bedrock       = Mock()
            model_id      = random_text('random_model')
            body          = {'the': random_text('random_request')}
            response_data = {'the': random_text('random_response')}
            kwargs        = dict(bedrock=bedrock, model_id=model_id, body=body)

            bedrock.model_invoke.return_value = response_data
            self.bedrock_cache.model_invoke(**kwargs)


    # @trace_calls(ignore         = []    , include        = ['osbot_'], contains=[]                 ,
    #              source_code    = False , show_lines     = False ,
    #              show_duration  = True , duration_bigger_than = 0.001,
    #              show_class     = True , show_locals    = False ,
    #              show_types     = False  , show_internals = True , extra_data = False          ,
    #              show_types_padding = 100  , duration_padding=120,
    #              enabled        = False  )

    # Bedrock cache specific methods

    @pytest.mark.skip("Fix after refactoring of Sqlite__Cache__Requests has been completed")
    def test_comments(self):
        model_id = 'an_model_id'
        body     = {'an' : 'body'}
        comments = 'here are some comments'
        class An_Model(Kwargs_To_Self):
            model_id : str
            def body(self):
                return body

        an_model = An_Model(model_id=model_id)
        assert an_model.__locals__() == {'model_id': model_id}
        with self.bedrock_cache as _:
            request_data  = _.cache_request_data(model_id, body)
            response_data = {}
            _.cache_add(request_data, response_data )
            assert _.comments(an_model) is ''
            assert _.comments_set(an_model, comments).get('status') == 'ok'
            assert _.comments(an_model) == comments
            with Stdout() as stdout:
                _.comments_print(an_model)
            assert stdout.value() == ('\n'
                                      '\n'
                                      '----------------------------\n'
                                      f'comment on model: {model_id} "\n'
                                      '\n'
                                      f'{comments}\n')

    def test_requests_data__with_model_id(self):
        count = 2
        self.add_test_requests(count)
        with self.bedrock_cache as _:
            requests_data_by_model_id = _.requests_data__by_model_id()
            for model_id, requests_data in requests_data_by_model_id.items() :
                assert requests_data == _.requests_data__with_model_id(model_id)

    def test_requests_data__by_model_id(self):
        count = 2
        self.add_test_requests(count)
        with self.bedrock_cache as _:
            requests_data_by_model_id = _.requests_data__by_model_id()
            model_ids        = list_set(requests_data_by_model_id)
            model_id         = model_ids[0]
            requests_data    = requests_data_by_model_id.get(model_id)
            request_data     = requests_data[0]

            assert len(model_ids    )     == count
            assert len(requests_data)     == 1
            assert list_set(request_data) == ['_comments', '_hash', '_id', 'body', 'model']
            request_hash   = request_data.get('_hash')
            rows_with_hash = _.rows_where__request_hash(request_hash)
            row_with_hash  = rows_with_hash[0]
            response_data  = _.response_data_for__request_hash(request_hash)

            assert response_data        == from_json_str(row_with_hash.get('response_data'))
            assert len(rows_with_hash)  == 1
            assert from_json_str(row_with_hash.get('request_data')).get('model') == model_id

    # Bedrock overwrite methods
    def test_model_invoke(self):
        model_id             = 'aaaa'
        body                 = {'the': 'request data'}
        response_data        = {'the': 'return value'}
        request_data         = self.bedrock_cache.cache_request_data(model_id, body)                    # create object to tbe used to query cache
        new_row_obj          = self.bedrock_cache.create_new_cache_obj(request_data,response_data)      # get an object that is equal to the one that is going to be sent to the cache
        expected_cache_entry = { **new_row_obj.__locals__() ,                                           # extract its data , add the id and fix bug with bools
                                 'id'    : 1                }
        bedrock              = Mock()                                                                   # create Mock object to capture calls
        bedrock.model_invoke.return_value = response_data                                               # simulate return value from call to bedrock.model_invoke
        assert len(self.bedrock_cache.cache_entries()) == 0                                             # assert that before call assert there are no entries

        kwargs      = dict(bedrock=bedrock, model_id=model_id, body=body)                               # create object with params to call  model_invoke
        response_1  = self.bedrock_cache.model_invoke(**kwargs)                                         # make first call to model_invoke
        cache_entry = self.bedrock_cache.cache_entry(request_data)                                      # get cache entry

        assert response_1                              == response_data                                 # confirm response is what we expect (i.e. we got the value from bedrock.model_invoke.return_value
        assert cache_entry                             == expected_cache_entry                          # confirm that the cache obj is what we expect
        assert len(self.bedrock_cache.cache_entries()) == 1                                             # confirm we only have one entry in the cache
        assert self.bedrock_cache.cache_entries()      == [expected_cache_entry]                        # confirm the cache has the values we expect

        bedrock.model_invoke.assert_called_once()                                                       # confirm the invocation to the bedrock.model_invoke was only done once
        bedrock.model_invoke.assert_called_once_with(model_id=model_id, body=body)                                    #         and it had the expected params

        response_2 = self.bedrock_cache.model_invoke(**kwargs)                                          # make another call
        assert response_2 == response_1                                                                 # conform response is the same as the previous request
        bedrock.model_invoke.assert_called_once()                                                       # confirm there was no further call to bedrock.model_invoke
        assert len(self.bedrock_cache.cache_entries()) == 1                                             # assert we still only have one entry in the cache
        assert bedrock.model_invoke.call_count         == 1                                             # confirm we only had one call

        self.bedrock_cache.config.enabled = False                                                              # disable cache
        response_3 = self.bedrock_cache.model_invoke(**kwargs)                                          # make another call
        assert response_3 == response_1                                                                 # confirm the responses are still the same
        assert bedrock.model_invoke.call_count == 2                                                     # confirm that two calls were made to the bedrock.model_invoke method

        changed_response_data = {'the': 'changed value'}
        bedrock.model_invoke.return_value = changed_response_data                                       # change the mocked return value of bedrock.model_invoke
        response_4 = self.bedrock_cache.model_invoke(**kwargs)                                          # make another call to bedrock_cache.model_invoke
        assert response_4 != response_1                                                                 # where the response doesn't match the previous ones
        assert response_4 == changed_response_data                                                      # and match the newly set value
        assert bedrock.model_invoke.call_count == 3                                                     # confirm that there was another call to the bedrock.model_invoke method

        # note: this next tests show a behaviour that happens when the case is enabled and disabled (the disable mode does not touch the cache database)
        self.bedrock_cache.config.enabled = True                                                               # enable cache
        response_5 = self.bedrock_cache.model_invoke(**kwargs)                                          # make another call to bedrock_cache.model_invoke
        assert response_5 == response_1                                                                 # where we now get previous value (since that is the one that was cached
        assert response_5 != response_4                                                                 # and doesn't match the changed value
        assert bedrock.model_invoke.call_count == 3                                                     # confirm that there was NOT another call to the bedrock.model_invoke method
        assert len(self.bedrock_cache.cache_entries()) ==1                                              # confirm we have on entry in the cache
        assert self.bedrock_cache.delete_where_request_data(request_data) is True                       # confirm it was deleted ok
        assert self.bedrock_cache.delete_where_request_data(request_data) is False                      # trying to delete an entry that doesn't exist shouldn't work
        assert self.bedrock_cache.cache_entries() == []                                                 # confirm the cache file is empty again


    def test_models(self):
        request_data         = {'method': 'models'}
        response_data        = [0,1,2,3]
        new_cache_entry      = self.bedrock_cache.create_new_cache_row_data(request_data, response_data)
        expected_cache_entry = { **new_cache_entry,
                                 'comments'    : '' ,
                                 'id'          : 1  ,
                                 'metadata'    : '' ,
                                 'request_type': '' ,
                                 'source'      : '' ,
                                 'timestamp'   : 0  }
        bedrock = Mock()
        bedrock.models.return_value = response_data
        models                      = self.bedrock_cache.models(bedrock)

        assert models == response_data
        assert self.bedrock_cache.cache_entries() ==[expected_cache_entry]

