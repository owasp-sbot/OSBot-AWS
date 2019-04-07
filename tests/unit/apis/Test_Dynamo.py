import unittest
from aws.dynamo import *
#from pprint     import pformat

class Test_Dynamo(unittest.TestCase):
    def setUp(self):
        self.dynamo     = Dynamo()
        self.table_name = 'temp-table'
        self.table_key  = 'an_field'
        self.table      = Dynamo_Table(self.table_name,self.table_key)

    def test_create(self):
        if self.table.exists() is False:
            self.dynamo.create(self.table_name, 'an_field')
            assert self.table.exists()                       is True
            assert self.table.info()['Table']['TableName']   == self.table_name

    def test_list(self):
        result = self.dynamo.list()
        assert 'temp-table' in result

class Test_Dynamo_Table(unittest.TestCase):

    def setUp(self):
        self.table_name =  'temp-table'
        self.table_key  = 'an_field'
        self.table = Dynamo_Table(self.table_name, self.table_key)

    def test_add(self):
        self.table.add({ self.table_key : 'key-1', 'answer-1': 42 })
        self.table.add({ self.table_key : 'key-2', 'answer-2': -1  })

    def test_add_delete_batch(self):
        items = [{ self.table_key: 'key-3', 'answer-1': 42 },
                 { self.table_key: 'key-4', 'answer-1': 42 }]
        self.table.add_batch(items)
        keys = self.table.keys()
        assert len(keys) == 4
        assert 'key-3'   in  keys

        items = [ { self.table_key: 'key-3'},
                  { self.table_key: 'key-4' }]
        self.table.delete_batch(items)

        keys = self.table.keys()
        assert len(keys) == 2

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


    # Use cases
    def test_5k_ips(self):
        table = Dynamo_Table('test-table','ip')
        keys = table.keys()
        assert len(keys) == 5044
        results = table.get_batch(keys)
        assert len(next(results)) == 100


class Test_Dynamo_Delete(unittest.TestCase):
    def setUp(self):
        self.dynamo     = Dynamo()
        self.table_name = 'temp-table'
        self.table_key  = 'an_field'
        self.table      = Dynamo_Table(self.table_name,self.table_key)

    def test_xyz_delete(self):                      # run this one last
        if self.table.exists():
            self.dynamo.delete(self.table_name)
            assert self.table.exists() is False
            assert self.table.info()   is None

if __name__ == '__main__':
    unittest.main()