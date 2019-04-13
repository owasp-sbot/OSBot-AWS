import unittest
#from pprint     import pformat
from time import sleep

from pbx_gs_python_utils.utils.Dev import Dev
from pbx_gs_python_utils.utils.Misc import Misc

from osbot_aws.apis.Dynamo import Dynamo, Dynamo_Table

# class Test_Dynamo(unittest.TestCase):
#     def setUp(self):
#         self.dynamo     = Dynamo()
#         self.table_name = 'temp-table'
#         self.table_key  = 'an_field'
#         self.table      = Dynamo_Table(self.table_name,self.table_key)
#
#     def test_create(self):
#         if self.table.exists() is False:
#             self.dynamo.create(self.table_name, 'an_field')
#             assert self.table.exists()                       is True
#             assert self.table.info()['Table']['TableName']   == self.table_name
#
#     def test_list(self):
#         result = self.dynamo.list()
#         assert 'temp-table' in result

class test_Dynamo(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        dynamo = Dynamo()
        table_name = 'temp-table'
        table_key = 'an_field'
        table = Dynamo_Table(table_name, table_key)

        if table.exists() is False:
            dynamo.create(table_name, 'an_field')
            assert table.exists() is True
            assert table.info()['Table']['TableName'] == table_name

        assert 'temp-table' in dynamo.list()

    @classmethod
    def tearDownClass(cls):
        dynamo = Dynamo()
        table_name = 'temp-table'
        table_key = 'an_field'
        table = Dynamo_Table(table_name, table_key)

        if table.exists():
            dynamo.delete(table_name)
            assert table.exists() is False
            assert table.info()   is None

    def setUp(self):
        self.table_name =  'temp-table'
        self.table_key  = 'an_field'
        self.table = Dynamo_Table(self.table_name, self.table_key)

    def test_add(self):
        self.table.add({ self.table_key : 'key-1', 'answer-1': 42 })
        self.table.add({ self.table_key : 'key-2', 'answer-2': -1  })

    def test_add_delete_batch(self):
        assert self.table.keys() == ['key-2', 'key-1']
        items = [{ self.table_key: 'key-3', 'answer-1': 42 },
                 { self.table_key: 'key-4', 'answer-1': 42 }]
        self.table.add_batch(items)
        keys = self.table.keys(use_cache=False)
        assert len(keys) == 4
        assert 'key-3'   in  keys

        items = [ { self.table_key: 'key-3'},
                  { self.table_key: 'key-4' }]
        self.table.delete_batch(items)

        keys = self.table.keys()
        assert len(keys) == 4

    def test_delete(self):
        self.table.add({self.table_key: 'key-5', 'answer-1': 42})
        assert self.table.get('key-5') == {self.table_key: 'key-5', 'answer-1': 42}

        self.table.delete('key-5')
        assert self.table.get('key-5') == None

    def test_keys(self):
        result = self.table.keys()
        assert result == ['key-2', 'key-1']

    def test_info(self):
        result = self.table.info()
        assert result['Table']['AttributeDefinitions'] == [{'AttributeName': 'an_field', 'AttributeType': 'S'}]
        assert result['Table']['TableName'           ] == self.table_name

    def test_get(self):
        result = self.table.get('key-1')
        assert result == {'answer-1': 42, 'an_field': 'key-1'}

    def test_get_batch(self):
        self.table.chuck_size = 1
        keys = self.table.keys()
        results = self.table.get_batch(keys)

        assert next(results) == [{'answer-2': -1, 'an_field': 'key-2'}]
        assert next(results) == [{'answer-1': 42, 'an_field': 'key-1'}]

    def test_status(self):
        assert self.table.status() == 'ACTIVE'

# this is not working as expected (namely the `test_streams` part)
@unittest.skip
class test_Dynamo_Streams(unittest.TestCase):

    def setUp(self):
        self.table_name        = 'temp-table-with-streams'  #Misc.random_string_and_numbers(prefix='temp-table-with-streams_')
        self.table_key         = 'an_field'
        with_streams      = True
        self.dynamo_table = Dynamo_Table(self.table_name, self.table_key)
        self.dynamo       = Dynamo()
        if self.dynamo_table.exists() is False:
            self.dynamo.create(self.table_name, self.table_key, with_streams)

    def test_stream_arn(self):
        assert self.dynamo_table.stream_arn().startswith('arn:aws:dynamodb:') is True

    def test_stream_info(self):
        Dev.pprint(self.dynamo_table.stream_info())

    def test_stream_get_data_latest(self):
        self.dynamo_table.add({ self.table_key : 'key-1', 'answer-1': 42 })
        Dev.pprint(self.dynamo_table.stream_get_data_latest())

    def test_streams(self):
        assert len(self.dynamo.streams()) > 1



# class Test_Dynamo_Delete(unittest.TestCase):
#     def setUp(self):
#         self.dynamo     = Dynamo()
#         self.table_name = 'temp-table'
#         self.table_key  = 'an_field'
#         self.table      = Dynamo_Table(self.table_name,self.table_key)
#
#     def test_xyz_delete(self):                      # run this one last
#         if self.table.exists():
#             self.dynamo.delete(self.table_name)
#             assert self.table.exists() is False
#             assert self.table.info()   is None
#
# if __name__ == '__main__':
#     unittest.main()