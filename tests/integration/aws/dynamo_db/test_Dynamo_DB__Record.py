from osbot_aws.aws.dynamo_db.Dynamo_DB__Record                      import Dynamo_DB__Record, Dynamo_DB__Record__Metadata
from osbot_utils.utils.Misc                                         import str_to_bytes
from tests.integration.aws.dynamo_db.TestCase__Temp_Dynamo_DB_Table import TestCase__Temp_Dynamo_DB_Table

TEST_TABLE_NAME = 'temp_table__test_Dynamo_DB__Record'

class test_Dynamo_DB__Record(TestCase__Temp_Dynamo_DB_Table):

    @classmethod
    def setUpClass(cls):
        cls.table_name = TEST_TABLE_NAME
        super().setUpClass()

    def setUp(self):
        self.db_record = Dynamo_DB__Record()

    def test__init__(self):
        table_info = self.dynamo_db.table_info(TEST_TABLE_NAME)
        assert table_info.get('TableArn'  ) == 'arn:aws:dynamodb:ddblocal:000000000000:table/temp_table__test_Dynamo_DB__Record'
        assert table_info.get('TableName'  ) =='temp_table__test_Dynamo_DB__Record'
        assert table_info.get('TableStatus') == 'ACTIVE'

        assert self.table.table_name == TEST_TABLE_NAME
        expected_locals = dict(data={}, data_binary=b'', key_value='',metadata=self.db_record.metadata)
        assert type(self.db_record.metadata) is Dynamo_DB__Record__Metadata
        assert self.db_record.__locals__()   == expected_locals
        assert self.table.exists()           == {'data': True, 'status': 'ok'}

    
    def test_add_record(self):
        with self.table as _:
            result      = _.add_record(self.db_record)
            document    = result.get('data').get('document')
            key_value   = document.get(self.key_name)
            assert result.get('status') == 'ok'
            assert document             == _.document(key_value).get('data')

            # new_record = Dynamo_DB__Record().deserialize_from_dict(document)      # todo: fix this test, since the key_name is not added automatically (since it doesn't exist in the schema)
            # assert new_record.serialize_to_dict() == document
            self.table.clear_table()

    def test_compress_binary_data(self):
        data = 'hello world' * 10
        self.db_record.set_binary_data__from_str(data)
        assert self.db_record.data_binary == str_to_bytes(data)
        self.db_record.compress_binary_data()
        assert self.db_record.data_binary != str_to_bytes(data)
        self.db_record.uncompress_binary_data()
        assert self.db_record.data_binary == str_to_bytes(data)

    def test_set_bynary_data__from_dict(self):
        data_as_dict = {'a': 1, 'b': 2}
        assert self.db_record.set_binary_data__from_dict(data_as_dict).data_binary == b'{"a": 1, "b": 2}'

    def test_set_bynary_data__from_str(self):
        data_as_str = 'hello world'
        assert self.db_record.set_binary_data__from_str(data_as_str).data_binary == b'hello world'


    def test_serialize_to_dict(self):
        self.db_record.metadata.created_by = 'unit test'
        self.db_record.data = {'anwser': 42}
        json_data = self.db_record.serialize_to_dict()
        assert json_data == { 'data': {'anwser': 42},
                              'data_binary': b'',
                              'key_value': '',
                              'metadata': { 'created_by': 'unit test',
                                            'timestamp_created': 0,
                                            'timestamp_updated': 0,
                                            'updated_by': ''}}

        new_obj = Dynamo_DB__Record().deserialize_from_dict(json_data)
        assert self.db_record.serialize_to_dict() ==  new_obj.serialize_to_dict()