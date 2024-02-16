from unittest import TestCase

from osbot_aws.aws.dynamo_db.Dynamo_DB__Record import Dynamo_DB__Record, Dynamo_DB__Record__Metadata
from osbot_aws.aws.dynamo_db.Dynamo_DB__Table import Dynamo_DB__Table
from osbot_utils.utils.Dev import pprint
from tests.integration.aws.dynamo_db.TestCase__Temp_Dynamo_DB_Table import TestCase__Temp_Dynamo_DB_Table
from tests.integration.aws.dynamo_db.test_Dynamo_DB import Dynamo_DB__with_temp_role

TEST_TABLE_NAME = 'temp_table__test_Dynamo_DB__Record'

class test_Dynamo_DB__Record(TestCase__Temp_Dynamo_DB_Table):

    @classmethod
    def setUpClass(cls):
        cls.remove_on_exit = False
        cls.table_name     = TEST_TABLE_NAME
        super().setUpClass()

    def setUp(self):
        self.db_record = Dynamo_DB__Record()

    def test__init__(self):
        assert self.table.table_name == TEST_TABLE_NAME
        expected_locals = dict(data={}, data_binary=b'', key_value='',metadata=self.db_record.metadata)
        assert type(self.db_record.metadata) is Dynamo_DB__Record__Metadata
        assert self.db_record.__locals__()   == expected_locals
        assert self.table.exists()           == {'data': True, 'status': 'ok'}

    def test_add_record(self):
        with self.table as _:
            result    = _.add_record(self.db_record)
            key_value = result.get('data').get('key_value')
            document  = result.get('data').get('document')
            assert result.get('status') == 'ok'
            assert document             == _.document(key_value).get('data')
            self.table.clear_table()
